from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict
from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import uuid

router = APIRouter(prefix="/calendar", tags=["calendar"])

# In-memory store for MVP
_calendars: Dict[str, dict] = {}

class CalendarCreate(BaseModel):
    owner_name: str
    owner_email: EmailStr
    timezone: str = "America/Los_Angeles"
    slot_minutes: int = 30
    work_start_hour: int = 9
    work_end_hour: int = 17

class Booking(BaseModel):
    name: str
    email: EmailStr
    start: datetime
    end: datetime

def get_tz(tz_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        # Fallback for containers without IANA db
        return ZoneInfo("UTC")

def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end

@router.post("", summary="Create a new calendar")
def create_calendar(cfg: CalendarCreate):
    if cfg.work_end_hour <= cfg.work_start_hour:
        raise HTTPException(status_code=400, detail="work_end_hour must be after work_start_hour")
    if cfg.slot_minutes not in (15, 20, 30, 45, 60):
        # Keep MVP simple; expand later
        raise HTTPException(status_code=400, detail="slot_minutes must be one of 15, 20, 30, 45, 60")

    cal_id = uuid.uuid4().hex[:8]
    _calendars[cal_id] = {
        "config": cfg.dict(),
        "bookings": []  # dicts: {name,email,start,end} (timezone-aware datetimes)
    }
    return {
        "id": cal_id,
        "booking_url": f"/calendar/{cal_id}/book",
        "owner": cfg.owner_name,
        "timezone": cfg.timezone
    }

@router.get("/{cal_id}/slots", summary="List available slots for a date")
def get_slots(cal_id: str, date_str: str):
    cal = _calendars.get(cal_id)
    if not cal:
        raise HTTPException(status_code=404, detail="Calendar not found")

    try:
        d = date.fromisoformat(date_str)  # YYYY-MM-DD
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")

    cfg = cal["config"]
    tz = get_tz(cfg["timezone"])

    start_dt = datetime(d.year, d.month, d.day, cfg["work_start_hour"], 0, tzinfo=tz)
    end_dt   = datetime(d.year, d.month, d.day, cfg["work_end_hour"],   0, tzinfo=tz)
    step = timedelta(minutes=cfg["slot_minutes"])

    # Candidates
    slots = []
    cur = start_dt
    while cur + step <= end_dt:
        slots.append({"start": cur.isoformat(), "end": (cur+step).isoformat()})
        cur += step

    # Remove conflicts
    booked = cal["bookings"]
    available = []
    for s in slots:
        s_start = datetime.fromisoformat(s["start"])
        s_end   = datetime.fromisoformat(s["end"])
        conflict = any(overlaps(s_start, s_end, b["start"], b["end"]) for b in booked)
        if not conflict:
            available.append(s)

    return {"cal_id": cal_id, "date": d.isoformat(), "slots": available}

@router.post("/{cal_id}/book", summary="Book a slot")
def book(cal_id: str, payload: Booking):
    cal = _calendars.get(cal_id)
    if not cal:
        raise HTTPException(status_code=404, detail="Calendar not found")

    cfg = cal["config"]
    tz  = get_tz(cfg["timezone"])

    # Normalize to calendar tz; if naive, assume calendar tz
    start = payload.start
    end   = payload.end
    if start.tzinfo is None:
        start = start.replace(tzinfo=tz)
    else:
        start = start.astimezone(tz)
    if end.tzinfo is None:
        end = end.replace(tzinfo=tz)
    else:
        end = end.astimezone(tz)

    if end <= start:
        raise HTTPException(status_code=400, detail="end must be after start")

    slot = timedelta(minutes=cfg["slot_minutes"])
    if (start.minute % cfg["slot_minutes"] != 0) or ((end - start) != slot):
        raise HTTPException(status_code=400, detail=f"slot must be {cfg['slot_minutes']} minutes and aligned to the grid")

    # Check work hours in local time
    work_start = time(hour=cfg["work_start_hour"])
    work_end   = time(hour=cfg["work_end_hour"])
    if not (work_start <= start.timetz().replace(tzinfo=None) <= work_end and
            work_start <= (end - timedelta(seconds=1)).timetz().replace(tzinfo=None) <= work_end):
        raise HTTPException(status_code=400, detail="time is outside working hours")

    # Conflicts
    for b in cal["bookings"]:
        if overlaps(start, end, b["start"], b["end"]):
            raise HTTPException(status_code=409, detail="slot already booked")

    cal["bookings"].append({
        "name": payload.name,
        "email": payload.email,
        "start": start,
        "end": end
    })

    return {
        "status": "confirmed",
        "cal_id": cal_id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "attendee": {"name": payload.name, "email": payload.email}
    }

@router.get("/{cal_id}/bookings", summary="List bookings")
def list_bookings(cal_id: str):
    cal = _calendars.get(cal_id)
    if not cal:
        raise HTTPException(status_code=404, detail="Calendar not found")
    out = []
    for b in cal["bookings"]:
        out.append({
            "name": b["name"],
            "email": b["email"],
            "start": b["start"].isoformat(),
            "end": b["end"].isoformat(),
        })
    return {"cal_id": cal_id, "bookings": out}
