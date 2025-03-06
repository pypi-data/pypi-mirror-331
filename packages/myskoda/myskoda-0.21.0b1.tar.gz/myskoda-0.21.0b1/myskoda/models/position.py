"""Models for responses of api/v2/vehicle-status/{vin}/driving-range."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .common import Address, Coordinates


class PositionType(StrEnum):
    VEHICLE = "VEHICLE"


@dataclass
class Position(DataClassORJSONMixin):
    address: Address
    gps_coordinates: Coordinates = field(metadata=field_options(alias="gpsCoordinates"))
    type: PositionType


class ErrorType(StrEnum):
    VEHICLE_IN_MOTION = "VEHICLE_IN_MOTION"
    VEHICLE_POSITION_UNAVAILABLE = "VEHICLE_POSITION_UNAVAILABLE"


@dataclass
class Error(DataClassORJSONMixin):
    type: ErrorType
    description: str


@dataclass
class Positions(DataClassORJSONMixin):
    """Positional information (GPS) for the vehicle and other things."""

    errors: list[Error]
    positions: list[Position]
    timestamp: datetime | None = field(default=None)
