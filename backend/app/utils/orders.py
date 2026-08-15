from decimal import Decimal

ACTIVE_ORDER_STATES = ("abierto", "en_preparacion", "listo", "entregado")
ORDER_TRANSITIONS = {
    "abierto": {"en_preparacion", "cancelado"},
    "en_preparacion": {"listo", "cancelado"},
    "listo": {"entregado", "cancelado"},
    "entregado": {"cerrado"},
    "cerrado": set(), "cancelado": set(),
}


def recalculate_order(order):
    order.total = sum((item.subtotal for item in order.items), Decimal("0.00"))

