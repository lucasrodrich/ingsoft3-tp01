from datetime import date, time

import pytest

from app.utils.reservations import reservations_overlap

HOY = date(2026, 10, 1)


@pytest.mark.parametrize("hora_reserva_b,se_solapan", [
    (time(20, 0), True),    # misma hora exacta
    (time(21, 30), True),   # empieza 90 min después: todavía dentro de la ventana de 120 min
    (time(22, 0), False),   # empieza justo a los 120 min: el borde -- ya NO se solapa
    (time(18, 0), False),   # termina justo cuando arranca la otra: tampoco se solapa
])
def test_reservas_en_la_misma_mesa_se_solapan_segun_la_ventana_de_120_minutos(hora_reserva_b, se_solapan):
    assert reservations_overlap(HOY, time(20, 0), HOY, hora_reserva_b) is se_solapan
