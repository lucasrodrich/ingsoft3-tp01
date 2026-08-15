from datetime import date, timedelta


def test_reservation_conflicts_capacity_and_transitions(client, register):
    _, h=register(); table=client.post("/api/mesas",json={"numero":1,"capacidad":4},headers=h).json(); future=(date.today()+timedelta(days=2)).isoformat()
    base={"nombreCliente":"Cliente Uno","cantidadPersonas":4,"fecha":future,"hora":"20:00","mesaId":table["id"]}
    first=client.post("/api/reservas",json=base,headers=h); assert first.status_code==201
    assert client.post("/api/reservas",json={**base,"nombreCliente":"Otro","hora":"21:00"},headers=h).status_code==409
    assert client.post("/api/reservas",json={**base,"nombreCliente":"Otro","hora":"22:00"},headers=h).status_code==201
    assert client.post("/api/reservas",json={**base,"cantidadPersonas":5,"hora":"18:00"},headers=h).status_code==400
    rid=first.json()["id"]
    assert client.patch(f"/api/reservas/{rid}/estado",json={"estado":"confirmada"},headers=h).status_code==200
    assert client.patch(f"/api/reservas/{rid}/estado",json={"estado":"pendiente"},headers=h).status_code==400
    assert client.patch(f"/api/reservas/{rid}/estado",json={"estado":"cancelada"},headers=h).status_code==200
    assert client.post("/api/reservas",json={**base,"nombreCliente":"Liberado","hora":"20:00"},headers=h).status_code==201


def test_past_reservation_rejected(client, register):
    _,h=register();table=client.post("/api/mesas",json={"numero":1,"capacidad":4},headers=h).json()
    response=client.post("/api/reservas",json={"nombreCliente":"Cliente","cantidadPersonas":2,"fecha":(date.today()-timedelta(days=1)).isoformat(),"hora":"20:00","mesaId":table["id"]},headers=h)
    assert response.status_code==400


def test_ownership_is_hidden_and_dashboard_isolated(client, register):
    _,a=register("a@example.com");_,b=register("b@example.com","Usuario B")
    table=client.post("/api/mesas",json={"numero":1,"capacidad":4},headers=a).json();cat=client.get("/api/categorias",headers=a).json()[0]
    product=client.post("/api/productos",json={"nombre":"Propio","precio":100,"categoriaId":cat["id"]},headers=a).json()
    order=client.post("/api/pedidos",json={"mesaId":table["id"]},headers=a).json();future=(date.today()+timedelta(days=1)).isoformat()
    reservation=client.post("/api/reservas",json={"nombreCliente":"Cliente A","cantidadPersonas":2,"fecha":future,"hora":"20:00","mesaId":table["id"]},headers=a).json()
    for path in (f"/api/mesas/{table['id']}",f"/api/productos/{product['id']}",f"/api/pedidos/{order['id']}",f"/api/reservas/{reservation['id']}"):
        assert client.get(path,headers=b).status_code==404
    assert client.post("/api/pedidos",json={"mesaId":table["id"]},headers=b).status_code==404
    assert client.post(f"/api/pedidos/{order['id']}/items",json={"productoId":product["id"],"cantidad":1},headers=b).status_code==404
    assert client.get("/api/dashboard",headers=b).json()["mesasOcupadas"]==0
    assert client.get("/api/dashboard",headers=a).json()["pedidosAbiertos"]==1


def test_health(client):
    assert client.get("/health").json()=={"status":"healthy"}
