from app.auth.password import hash_password, verify_password


def test_hash_password_permite_verificar_la_misma_contrasena():
    # Arrange
    contrasena = "password123"

    # Act
    hash_generado = hash_password(contrasena)

    # Assert
    assert verify_password(contrasena, hash_generado) is True


def test_verify_password_rechaza_una_contrasena_incorrecta():
    hash_generado = hash_password("password123")

    assert verify_password("otra-contrasena", hash_generado) is False
