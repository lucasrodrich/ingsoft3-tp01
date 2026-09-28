from decimal import Decimal
from types import SimpleNamespace

from app.utils.orders import recalculate_order


def test_recalculate_order_suma_los_subtotales_de_todos_los_items():
    # Arrange: un pedido "fake" -- no hace falta la base de datos, solo objetos
    # con los atributos que recalculate_order() lee (item.subtotal) y escribe (order.total).
    pedido = SimpleNamespace(items=[
        SimpleNamespace(subtotal=Decimal("1000.00")),
        SimpleNamespace(subtotal=Decimal("500.50")),
    ], total=None)

    # Act: la función bajo prueba
    recalculate_order(pedido)

    # Assert
    assert pedido.total == Decimal("1500.50")


def test_recalculate_order_sin_items_da_total_cero():
    # Caso de borde: un pedido recién creado, sin items todavía.
    pedido = SimpleNamespace(items=[], total=None)

    recalculate_order(pedido)

    assert pedido.total == Decimal("0.00")
