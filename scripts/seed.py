"""Create the schema and load synthetic data.

Assumes an empty database. If you need to re-seed, reset first:
    docker compose down -v && docker compose up -d
"""

from datetime import UTC, datetime, timedelta

from agent_runtime.db import SessionLocal, engine
from agent_runtime.models import Appointment, Base, Customer, Professional, Service, Slot

SLOT_DURATION = timedelta(minutes=30)
WORK_START_HOUR = 9
WORK_END_HOUR = 18
DAYS_AHEAD = 14


def _generate_slots(professional_id: str, start_date: datetime) -> list[Slot]:
    """One slot per 30-minutes block, business hours, for DAYS_AHEAD days."""
    slots = []
    for day_offset in range(DAYS_AHEAD):
        day = start_date + timedelta(days=day_offset)
        current = day.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
        end_of_day = day.replace(hour=WORK_END_HOUR, minute=0, second=0, microsecond=0)

        while current < end_of_day:
            slots.append(
                Slot(
                    professional_id=professional_id,
                    starts_at=current,
                    ends_at=current + SLOT_DURATION,
                )
            )
            current += SLOT_DURATION

    return slots


def main() -> None:
    Base.metadata.create_all(engine)
    print("schema created")

    with SessionLocal() as session:
        cleaning = Service(name="cleaning", duration_minutes=30)
        checkup = Service(name="checkup", duration_minutes=30)
        session.add_all([cleaning, checkup])

        ana = Professional(name="Dr Ana Test")
        carlos = Professional(name="Dr. Carlos Test")
        session.add_all([ana, carlos])

        session.flush()

        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        slots = _generate_slots(ana.id, today) + _generate_slots(carlos.id, today)
        session.add_all(slots)

        alice = Customer(name="Alice Silva Test", phone="+5511999990001")
        bruno = Customer(name="Bruno Costa Test", phone="+5511999990002")
        session.add_all([alice, bruno])

        session.flush()

        already_booked = Appointment(
            slot_id=slots[0].id, customer_id=alice.id, service_id=cleaning.id
        )

        session.add(already_booked)

        session.commit()
        print(f"seeded {len(slots)} slots, 2 services, 2 professionals, 2 customers, 1 appointment")


if __name__ == "__main__":
    main()
