from typing import Annotated

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from simula_ligths_api.lights import async_lights

app = FastAPI()


class BrightnessValue(BaseModel):
    value: Annotated[
        int, Field(strict=True, ge=0, le=4)
    ]  # Add validation for range if necessary


class ColorValue(BaseModel):
    value: Annotated[
        int, Field(strict=True, ge=0, le=4)
    ]  # Add validation for color format if necessary


@app.post("/lights/{room}/brightness")
async def set_brightness(room: int, brightness: BrightnessValue):
    # Implement brightness control logic
    try:
        await async_lights(room=room, button="brightness", index=brightness.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "status": "success",
        "room": room,
        "operation": "set_brightness",
        "value": brightness.value,
    }


@app.post("/lights/{room}/color")
async def set_color(room: int, color: ColorValue):
    # Implement color control logic
    await async_lights(room=room, button="color", index=color.value)
    return {
        "status": "success",
        "room": room,
        "operation": "set_color",
        "value": color.value,
    }
