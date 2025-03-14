"""
Usage:

You must give your office number as the first argument:

    lights.py ROOM

With no other arguments, the lights are reset:

    lights.py ROOM

You can also specify brightness or color with a range 0-4:

    lights.py ROOM brightness 2

    lights.py ROOM color 3
"""

import sys
import time
from enum import Enum
from typing import Optional
from io import BytesIO

import typer
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

def setup_page(url: str):
    """Connect to the light-control page using Playwright"""
    print(f"Connecting to {url}")
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    # Create a new browser context with a fixed viewport size
    context = browser.new_context(viewport={"width": 500, "height": 500})
    page = context.new_page()
    page.goto(url, timeout=10000)  # 10 seconds timeout
    return page, browser, playwright

def room_url(room: int) -> str:
    """Get the light control URL for a given office number"""
    if room < 300:
        ip = "172.16.4.61"
    elif 300 <= room < 400:
        ip = "172.16.4.62"
    else:
        ip = "172.16.4.63"
    return f"http://{ip}/webvisu/rom{room}.htm"

# Relative positions of buttons that scale with the screen size
locations = {
    # brightness
    "reset": (0.5, 0.625),
    "brightness": [(x, 0.7) for x in (0.1, 0.3, 0.5, 0.7, 0.9)],
    "color": [(x, 0.9) for x in (0.1, 0.3, 0.5, 0.7, 0.9)],
}

def get_screen(page) -> np.ndarray:
    """Get the current screen as an RGB numpy array"""
    png = page.screenshot()
    im = Image.open(BytesIO(png))
    return np.asarray(im, dtype=np.uint8)[:, :, :3]  # drop any alpha channel

def wait_for_page(page):
    """
    Wait for the app to load by checking the screenshot.
    
    The loading screen is mostly white, so wait until less than 50% of pixels are white.
    """
    white_fraction = 1.0
    print("Waiting for page to load...", end="")
    while white_fraction > 0.5:
        screen = get_screen(page)
        white_fraction = (screen.mean(axis=2) == 255).mean()
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.1)
    print("ok")

def click_location(page, location_name: str, index: Optional[int] = None):
    """Click a given location on the app using relative coordinates."""
    canvas = page.query_selector("#foreground")
    if not canvas:
        print("Could not find the canvas element with id 'foreground'")
        return
    bounding_box = canvas.bounding_box()
    if not bounding_box:
        print("Could not get bounding box of the canvas element")
        return

    width = bounding_box["width"]
    height = bounding_box["height"]

    loc_percent = locations[location_name]
    name = location_name
    if index is not None:
        loc_percent = loc_percent[index]
        name = f"{location_name}:{index}"
    elif isinstance(loc_percent, list):
        # default to the middle option
        loc_percent = loc_percent[2]
    x = bounding_box["x"] + loc_percent[0] * width
    y = bounding_box["y"] + loc_percent[1] * height

    print(f"Clicking {name} (location percentages: {loc_percent})")
    page.mouse.click(x, y)

class Operation(str, Enum):
    reset = "reset"
    brightness = "brightness"
    color = "color"

app = typer.Typer()

@app.command()
def lights(
    room: int,
    button: Operation = Operation.reset,
    index: Optional[int] = None,
):
    """
    Interact with the lights for ROOM.

    If only the room number is specified, the brightness reset button is chosen.
    For multi-value buttons (e.g. brightness, color), an INDEX [0-4] can select which button.
    """
    page, browser, playwright = setup_page(room_url(room))
    wait_for_page(page)
    click_location(page, button, index)
    # Allow time for the event to register before closing
    time.sleep(1)
    browser.close()
    playwright.stop()

if __name__ == "__main__":
    app()

