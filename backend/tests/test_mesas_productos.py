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


def test_mesa_delete_blocked_by_pending_activity_then_by_history_then_allowed(client, register):
    # Regla real que el reporte de coverage mostró SIN NINGÚN test: DELETE /api/mesas/{id}
    # (app/routers/mesas.py líneas 66-74) nunca se ejecutaba en la suite.
    _, h = register()
    table = client.post("/api/mesas", json={"numero": 1, "capacidad": 4}, headers=h).json()
    cat = client.get("/api/categorias", headers=h).json()[0]
    product = client.post("/api/productos", json={"nombre": "Milanesa", "precio": 1000, "categoriaId": cat["id"]}, headers=h).json()
    order = client.post("/api/pedidos", json={"mesaId": table["id"]}, headers=h).json()

    # Con un pedido abierto: "actividad pendiente" (primer if del endpoint)
    assert client.delete(f"/api/mesas/{table['id']}", headers=h).status_code == 409

    # Cerramos el pedido: ya no hay actividad pendiente, pero sí historial (segundo if)
    client.post(f"/api/pedidos/{order['id']}/items", json={"productoId": product["id"], "cantidad": 1}, headers=h)
    for state in ("en_preparacion", "listo", "entregado", "cerrado"):
        client.patch(f"/api/pedidos/{order['id']}/estado", json={"estado": state}, headers=h)
    assert client.delete(f"/api/mesas/{table['id']}", headers=h).status_code == 409

    # Una mesa sin ningún pedido ni reserva sí se puede borrar (camino de éxito, 204)
    empty_table = client.post("/api/mesas", json={"numero": 2, "capacidad": 2}, headers=h).json()
    assert client.delete(f"/api/mesas/{empty_table['id']}", headers=h).status_code == 204

