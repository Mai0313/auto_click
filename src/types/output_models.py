from pydantic import BaseModel


class ShiftPosition(BaseModel):
    shift_x: int
    shift_y: int
