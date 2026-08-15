def test_tables_validation_unique_and_per_user(client, register):
    _, a = register("a@example.com")
    _, b = register("b@example.com", "Usuario B")
    assert client.post("/api/mesas", json={"numero":1,"capacidad":4}, headers=a).status_code == 201
    assert client.post("/api/mesas", json={"numero":1,"capacidad":4}, headers=a).status_code == 409
    assert client.post("/api/mesas", json={"numero":1,"capacidad":4}, headers=b).status_code == 201
    for body in ({"numero":0,"capacidad":4},{"numero":2,"capacidad":0},{"numero":2,"capacidad":-1}):
        assert client.post("/api/mesas", json=body, headers=a).status_code == 422


def test_products_crud_filters_and_category_ownership(client, register):
    _, a = register("a@example.com"); _, b = register("b@example.com", "Usuario B")
    cat_a = client.get("/api/categorias", headers=a).json()[0]
    cat_b = client.get("/api/categorias", headers=b).json()[0]
    product = client.post("/api/productos", json={"nombre":"Milanesa","precio":"1000.50","categoriaId":cat_a["id"]}, headers=a)
    assert product.status_code == 201
    assert client.post("/api/productos", json={"nombre":"Mal","precio":0,"categoriaId":cat_a["id"]}, headers=a).status_code == 422
    assert client.post("/api/productos", json={"nombre":"Ajeno","precio":10,"categoriaId":cat_b["id"]}, headers=a).status_code == 404
    assert len(client.get("/api/productos?texto=MILA&disponible=true", headers=a).json()) == 1
    pid = product.json()["id"]
    assert client.patch(f"/api/productos/{pid}/disponibilidad", json={"disponible":False}, headers=a).json()["disponible"] is False


def test_category_with_products_cannot_be_deleted(client, register):
    _, h = register(); cat = client.get("/api/categorias", headers=h).json()[0]
    client.post("/api/productos", json={"nombre":"Producto","precio":10,"categoriaId":cat["id"]}, headers=h)
    assert client.delete(f"/api/categorias/{cat['id']}", headers=h).status_code == 409

