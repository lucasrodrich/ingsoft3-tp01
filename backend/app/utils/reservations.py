from datetime import datetime, timedelta

BLOCKING_RESERVATION_STATES = ("pendiente", "confirmada")
RESERVATION_TRANSITIONS = {
    "pendiente": {"confirmada", "cancelada"},
    "confirmada": {"completada", "cancelada"},
    "cancelada": set(), "completada": set(),
}


def reservations_overlap(date_a, time_a, date_b, time_b):
    start_a = datetime.combine(date_a, time_a)
    start_b = datetime.combine(date_b, time_b)
    return start_a < start_b + timedelta(minutes=120) and start_b < start_a + timedelta(minutes=120)

