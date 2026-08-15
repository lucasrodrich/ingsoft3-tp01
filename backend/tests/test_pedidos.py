def setup_order(client, register):
    _, h = register(); table = client.post("/api/mesas",json={"numero":1,"capacidad":4},headers=h).json()
    cat = client.get("/api/categorias",headers=h).json()[0]
    product = client.post("/api/productos",json={"nombre":"Milanesa","precio":"1000.00","categoriaId":cat["id"]},headers=h).json()
    order = client.post("/api/pedidos",json={"mesaId":table["id"]},headers=h).json()
    return h, table, product, order


def test_order_lifecycle_totals_and_historical_price(client, register):
    h, table, product, order = setup_order(client, register)
    assert client.get(f"/api/mesas/{table['id']}",headers=h).json()["estado"] == "ocupada"
    assert client.post("/api/pedidos",json={"mesaId":table["id"]},headers=h).status_code == 409
    added = client.post(f"/api/pedidos/{order['id']}/items",json={"productoId":product["id"],"cantidad":2},headers=h).json()
    assert added["items"][0]["subtotal"] == 2000 and added["total"] == 2000
    client.put(f"/api/productos/{product['id']}",json={"nombre":"Milanesa","precio":"1500","categoriaId":product["categoriaId"],"disponible":True},headers=h)
    historical = client.get(f"/api/pedidos/{order['id']}",headers=h).json()
    assert historical["items"][0]["precioUnitario"] == 1000
    item = historical["items"][0]
    changed = client.put(f"/api/pedidos/{order['id']}/items/{item['id']}",json={"cantidad":3},headers=h).json()
    assert changed["total"] == 3000
    for state in ("en_preparacion","listo","entregado","cerrado"):
        response = client.patch(f"/api/pedidos/{order['id']}/estado",json={"estado":state},headers=h); assert response.status_code == 200
    assert client.get(f"/api/mesas/{table['id']}",headers=h).json()["estado"] == "disponible"
    assert client.put(f"/api/pedidos/{order['id']}/items/{item['id']}",json={"cantidad":2},headers=h).status_code == 409
    assert client.delete(f"/api/productos/{product['id']}",headers=h).status_code == 409


def test_item_delete_recalculates_and_cancel_releases_table(client, register):
    h, table, product, order = setup_order(client, register)
    data=client.post(f"/api/pedidos/{order['id']}/items",json={"productoId":product["id"],"cantidad":2},headers=h).json()
    emptied=client.delete(f"/api/pedidos/{order['id']}/items/{data['items'][0]['id']}",headers=h).json()
    assert emptied["total"] == 0
    assert client.patch(f"/api/pedidos/{order['id']}/estado",json={"estado":"listo"},headers=h).status_code == 400
    assert client.patch(f"/api/pedidos/{order['id']}/estado",json={"estado":"cancelado"},headers=h).status_code == 200
    assert client.get(f"/api/mesas/{table['id']}",headers=h).json()["estado"] == "disponible"

