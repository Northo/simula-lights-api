from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

app = FastAPI()

class BrightnessValue(BaseModel):
    value: int  # Add validation for range if necessary

class ColorValue(BaseModel):
    value: str  # Add validation for color format if necessary

@app.post("/lights/{room}/brightness")
async def set_brightness(room: str, brightness: BrightnessValue):
    # Implement brightness control logic
    return {
        "status": "success",
        "room": room,
        "operation": "set_brightness",
        "value": brightness.value
    }

@app.post("/lights/{room}/color")
async def set_color(room: str, color: ColorValue):
    # Implement color control logic
    return {
        "status": "success",
        "room": room,
        "operation": "set_color",
        "value": color.value
    }

