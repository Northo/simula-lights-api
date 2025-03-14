import sys
import asyncio
from contextlib import asynccontextmanager
from enum import Enum
from io import BytesIO
from typing import Optional, Tuple

import typer
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright, TimeoutError, Error


# --------------------------
# URL and Button Configurations
# --------------------------
def room_url(room: int) -> str:
    """Return the light control URL for a given office number."""
    if room < 300:
        ip = "172.16.4.61"
    elif 300 <= room < 400:
        ip = "172.16.4.62"
    else:
        ip = "172.16.4.63"
    return f"http://{ip}/webvisu/rom{room}.htm"


# Relative positions of buttons (scaling with screen dimensions)
locations = {
    "reset": (0.5, 0.625),
    "brightness": [(x, 0.7) for x in (0.1, 0.3, 0.5, 0.7, 0.9)],
    "color": [(x, 0.9) for x in (0.1, 0.3, 0.5, 0.7, 0.9)],
}


class Operation(str, Enum):
    reset = "reset"
    brightness = "brightness"
    color = "color"


# --------------------------
# Async Page Lifecycle Context Manager
# --------------------------
@asynccontextmanager
async def get_page(
    url: str, headless: bool = True, viewport: Tuple[int, int] = (500, 500)
):
    """
    Async context manager that launches Playwright, opens a new page to the given URL,
    and ensures the browser is closed upon exit.
    """
    print(f"Connecting to {url}")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": viewport[0], "height": viewport[1]}
        )
        page = await context.new_page()
        try:
            await page.goto(url, timeout=10000)  # 10 second timeout
            yield page
        finally:
            await browser.close()


# --------------------------
# Utility Functions
# --------------------------
async def get_screen(page) -> np.ndarray:
    """
    Capture a screenshot of the page and return it as an RGB NumPy array.
    """
    png = await page.screenshot()
    im = Image.open(BytesIO(png))
    return np.asarray(im, dtype=np.uint8)[:, :, :3]  # Drop alpha channel if present


async def wait_for_page(page):
    """
    Wait for the page to load by checking that the mostly white loading screen has cleared.
    """
    white_fraction = 1.0
    print("Waiting for page to load...", end="")
    while white_fraction > 0.5:
        screen = await get_screen(page)
        white_fraction = (screen.mean(axis=2) == 255).mean()
        sys.stdout.write(".")
        sys.stdout.flush()
        await asyncio.sleep(0.1)
    print(" ok")


async def click_location(page, location_name: str, index: Optional[int] = None):
    """
    Find the canvas with id 'foreground', compute the absolute click coordinates based on relative
    percentages, and perform a click.
    """
    canvas = await page.query_selector("#foreground")
    if not canvas:
        print("Could not find the canvas element with id 'foreground'")
        return
    bounding_box = await canvas.bounding_box()
    if not bounding_box:
        print("Could not retrieve bounding box for the canvas element")
        return

    width = bounding_box["width"]
    height = bounding_box["height"]

    loc_percent = locations[location_name]
    name = location_name
    if index is not None:
        loc_percent = loc_percent[index]
        name = f"{location_name}:{index}"
    elif isinstance(loc_percent, list):
        # Default to the middle option if no index is provided
        loc_percent = loc_percent[2]

    # Compute absolute x, y based on bounding box and relative percentages
    x = bounding_box["x"] + loc_percent[0] * width
    y = bounding_box["y"] + loc_percent[1] * height

    print(f"Clicking {name} (relative position: {loc_percent})")
    await page.mouse.click(x, y)

async def async_lights(
    room: int, button: Operation = Operation.reset, index: Optional[int] = None
):
    """
    Open the light control page for the specified room, wait for the app to load,
    and click the specified button.
    """
    url = room_url(room)
    try:
        async with get_page(url, headless=True) as page:
            await wait_for_page(page)
            await click_location(page, button, index)
            # Allow time for the event to register
            await asyncio.sleep(1)
    except (TimeoutError, Error) as e:
        print("An error occurred:", e)
        raise


app = typer.Typer()


@app.command()
def lights(
    room: int, button: Operation = Operation.reset, index: Optional[int] = None
):
    asyncio.run(async_lights(room, button, index))

if __name__ == "__main__":
    app()
