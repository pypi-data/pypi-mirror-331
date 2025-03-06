from typing import Tuple

from numpy._typing import ArrayLike
from pydantic import BaseModel, PositiveFloat, validator, field_validator


class CalibratedImage(BaseModel):
    data: ArrayLike
    spacing: Tuple[PositiveFloat, ...]
    offset: Tuple[int, ...]

    class Config:
        arbitrary_types_allowed = True

    def shape(self):
        return self.data.shape

    def get_corner_coordinates(self):
        return tuple(self.offset)

# TODO: Make Calibrated3DImage.mean() method
class Calibrated3DImage(CalibratedImage):
    offset: Tuple[int, int, int] = (0,) * 3

    @field_validator("data")
    def check_ndims(data: ArrayLike):
        assert data.ndim == 3, "Data must be 3D."
        return data


    class Config:
        arbitrary_types_allowed = True


class Calibrated2DImage(CalibratedImage):
    offset: Tuple[int, int] = (0,) * 2

    @field_validator("data")
    def check_ndims(data: ArrayLike):
        assert data.ndim == 2, "Data must be 2D."
        return data

    class Config:
        arbitrary_types_allowed = True


class Calibrated1DImage(CalibratedImage):
    offset: Tuple[int] = (0,)

    @field_validator("data")
    def check_ndims(data: ArrayLike):
        assert data.ndim == 1, "Data must be 1D."
        return data

    class Config:
        arbitrary_types_allowed = True
