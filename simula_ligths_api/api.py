from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field

from simula_ligths_api.lights import lights

app = FastAPI()

class BrightnessValue(BaseModel):
    value: Annotated[int, Field(strict=True, ge=0, le=4)]  # Add validation for range if necessary

class ColorValue(BaseModel):
    value: Annotated[int, Field(strict=True, ge=0, le=4)]  # Add validation for color format if necessary

@app.post("/lights/{room}/brightness")
async def set_brightness(room: str, brightness: BrightnessValue):
    # Implement brightness control logic
    lights(room=room, button="brightness", index=brightness)
    return {
        "status": "success",
        "room": room,
        "operation": "set_brightness",
        "value": brightness.value
    }

@app.post("/lights/{room}/color")
async def set_color(room: str, color: ColorValue):
    # Implement color control logic
    lights(room=room, button="color", index=color)
    return {
        "status": "success",
        "room": room,
        "operation": "set_color",
        "value": color.value
    }

