from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.jwt import create_access_token, get_current_user
from app.models import Usuario


def test_get_current_user_con_token_valido_busca_al_usuario_por_id_en_la_db():
    # Arrange: un usuario "fake" (no hace falta guardarlo de verdad) y su token real,
    # más un doble de la sesión de base de datos -- ésta es la dependencia externa
    # que reemplazamos para que el test no toque SQLite.
    usuario_autenticado = SimpleNamespace(id=42, email="a@example.com")
    token = create_access_token(usuario_autenticado)
    credenciales = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    db_doble = Mock()
    db_doble.get.return_value = usuario_autenticado

    # Act
    resultado = get_current_user(credentials=credenciales, db=db_doble)

    # Assert: dos cosas. Que devuelva el usuario correcto (como haría un stub)...
    assert resultado is usuario_autenticado
    # ...y que lo haya buscado de la forma correcta: por el modelo Usuario y el id
    # que venía adentro del token. Esto es lo que lo convierte en un MOCK y no en
    # un stub: no miramos solo el resultado, miramos CÓMO se usó la dependencia.
    db_doble.get.assert_called_once_with(Usuario, 42)


def test_get_current_user_sin_credenciales_lanza_401_sin_consultar_la_db():
    # Caso de error: sin token, la función tiene que rechazar ANTES de tocar la base.
    db_doble = Mock()

    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=None, db=db_doble)

    assert excinfo.value.status_code == 401
    db_doble.get.assert_not_called()
