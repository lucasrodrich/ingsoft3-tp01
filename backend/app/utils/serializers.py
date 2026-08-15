def user_json(user):
    return {"id": user.id, "nombre": user.nombre, "email": user.email, "createdAt": user.created_at.isoformat()}


def mesa_json(mesa):
    return {"id": mesa.id, "numero": mesa.numero, "capacidad": mesa.capacidad,
            "estado": mesa.estado, "createdAt": mesa.created_at.isoformat()}


def categoria_json(categoria):
    return {"id": categoria.id, "nombre": categoria.nombre, "createdAt": categoria.created_at.isoformat()}


def producto_json(producto):
    return {"id": producto.id, "nombre": producto.nombre, "descripcion": producto.descripcion,
            "precio": float(producto.precio), "disponible": producto.disponible,
            "categoriaId": producto.categoria_id, "categoriaNombre": producto.categoria.nombre,
            "createdAt": producto.created_at.isoformat(), "updatedAt": producto.updated_at.isoformat()}


def pedido_json(pedido):
    return {
        "id": pedido.id,
        "mesa": {"id": pedido.mesa.id, "numero": pedido.mesa.numero},
        "estado": pedido.estado,
        "items": [{
            "id": item.id, "productoId": item.producto_id,
            "productoNombre": item.producto.nombre, "cantidad": item.cantidad,
            "precioUnitario": float(item.precio_unitario), "subtotal": float(item.subtotal),
        } for item in pedido.items],
        "total": float(pedido.total), "createdAt": pedido.created_at.isoformat(),
        "updatedAt": pedido.updated_at.isoformat(),
        "closedAt": pedido.closed_at.isoformat() if pedido.closed_at else None,
    }


def reserva_json(reserva):
    return {"id": reserva.id, "nombreCliente": reserva.nombre_cliente,
            "cantidadPersonas": reserva.cantidad_personas, "fecha": reserva.fecha.isoformat(),
            "hora": reserva.hora.strftime("%H:%M"), "mesa": {"id": reserva.mesa.id, "numero": reserva.mesa.numero},
            "mesaId": reserva.mesa_id, "observaciones": reserva.observaciones, "estado": reserva.estado,
            "createdAt": reserva.created_at.isoformat(), "updatedAt": reserva.updated_at.isoformat()}

