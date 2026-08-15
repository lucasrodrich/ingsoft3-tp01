def test_register_creates_safe_user_and_categories(client, register):
    data, headers = register("  A@Example.com ")
    assert data["user"]["email"] == "a@example.com"
    assert "password" not in str(data["user"]).lower()
    categories = client.get("/api/categorias", headers=headers).json()
    assert [x["nombre"] for x in categories] == sorted(["Entradas", "Principales", "Pastas", "Pizzas", "Hamburguesas", "Bebidas", "Postres", "Otros"])


def test_register_validation_and_duplicate(client, register):
    register("same@example.com")
    assert client.post("/api/auth/register", json={"nombre":"X","email":"bad","password":"short"}).status_code == 422
    duplicate = client.post("/api/auth/register", json={"nombre":"Otro","email":"SAME@example.com","password":"password123"})
    assert duplicate.status_code == 409


def test_login_me_and_invalid_credentials(client, register):
    _, headers = register("login@example.com", password="password123")
    login = client.post("/api/auth/login", json={"email":"LOGIN@example.com","password":"password123"})
    assert login.status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/login", json={"email":"login@example.com","password":"incorrecta"}).status_code == 401
    assert client.post("/api/auth/login", json={"email":"none@example.com","password":"incorrecta"}).status_code == 401


def test_protected_routes_require_valid_jwt(client):
    assert client.get("/api/mesas").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization":"Bearer nonsense"}).status_code == 401

