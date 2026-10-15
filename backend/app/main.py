from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from .models import Appointment
from .schemas import AppointmentCreate, AppointmentOut, AppointmentUpdate, StatsOut


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Containers run Alembic before Uvicorn; create_all keeps tests self-contained.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def get_or_404(db: Session, appointment_id: int) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@app.get("/")
def root():
    return {"service": settings.app_name, "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(select(func.count(Appointment.id)))
    return {"status": "READY"}


@app.get("/api/appointments", response_model=list[AppointmentOut])
def list_appointments(db: Session = Depends(get_db)):
    return list(db.scalars(select(Appointment).order_by(Appointment.scheduled_at)))


@app.get("/api/appointments/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)
    ).all()
    counts = {s: c for s, c in rows}
    return StatsOut(
        total=sum(counts.values()),
        scheduled=counts.get("SCHEDULED", 0),
        checkedIn=counts.get("CHECKED_IN", 0),
        completed=counts.get("COMPLETED", 0),
        cancelled=counts.get("CANCELLED", 0),
    )


@app.get("/api/appointments/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, appointment_id)


@app.post("/api/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    appointment = Appointment(**payload.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@app.put("/api/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db)):
    appointment = get_or_404(db, appointment_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment


@app.delete("/api/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, appointment_id))
    db.commit()
