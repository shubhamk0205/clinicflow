from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["SCHEDULED", "CHECKED_IN", "COMPLETED", "CANCELLED"]
Department = Literal["GENERAL", "CARDIOLOGY", "DERMATOLOGY", "PEDIATRICS", "ORTHOPEDICS"]


class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=1, max_length=120)
    patient_phone: str = Field(default="", max_length=20)
    doctor: str = Field(min_length=1, max_length=120)
    department: Department = "GENERAL"
    scheduled_at: datetime
    reason: str = ""
    status: Status = "SCHEDULED"


class AppointmentUpdate(BaseModel):
    patient_name: str | None = Field(default=None, min_length=1, max_length=120)
    patient_phone: str | None = Field(default=None, max_length=20)
    doctor: str | None = Field(default=None, min_length=1, max_length=120)
    department: Department | None = None
    scheduled_at: datetime | None = None
    reason: str | None = None
    status: Status | None = None


class AppointmentOut(AppointmentCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StatsOut(BaseModel):
    total: int
    scheduled: int
    checkedIn: int
    completed: int
    cancelled: int
