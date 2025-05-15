from pydantic import BaseModel


class ShiftPosition(BaseModel):
    """Represents a shift in position.

    Attributes:
        shift_x (int): The amount to shift in the x-axis.
        shift_y (int): The amount to shift in the y-axis.
    """

    shift_x: int
    shift_y: int
