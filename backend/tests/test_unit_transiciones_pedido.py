import pytest

from app.utils.orders import ORDER_TRANSITIONS


@pytest.mark.parametrize("estado_actual,estado_siguiente", [
    ("abierto", "en_preparacion"),
    ("en_preparacion", "listo"),
    ("listo", "entregado"),
    ("entregado", "cerrado"),
])
def test_transicion_de_pedido_permitida_por_la_maquina_de_estados(estado_actual, estado_siguiente):
    # Act + Assert: no hay Arrange porque los datos entran directo por parámetro.
    assert estado_siguiente in ORDER_TRANSITIONS[estado_actual]


def test_transicion_de_pedido_no_permitida_es_rechazada():
    # Caso de error: "cerrado" es un estado terminal, no tiene ninguna transición
    # válida -- ni siquiera "volver a abrirlo".
    assert "abierto" not in ORDER_TRANSITIONS["cerrado"]
