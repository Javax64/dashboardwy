#
import requests
from django.utils import timezone
from django.db.models import Prefetch
#
from applications.productos.models import Producto
#
from .models import Sale, SaleDetail, CarShop


def procesar_venta(self, **params_venta):
    # recupera la lista de productos en carrtio
      # Filtra solo los productos del carrito activo del usuario
    productos_en_car = CarShop.objects.filter(cart__user=params_venta['user'], cart__is_active=True)
    
    productos_sin_stock = [] 
    if productos_en_car.count() > 0:
        # Primero, verificamos si hay algún producto sin stock suficiente
        for producto_car in productos_en_car:
            producto = producto_car.product
            if producto.count < producto_car.count:
                productos_sin_stock.append(producto.name)  # Agregar el nombre del producto
                continue
        # Si hay productos sin stock, no procesamos la venta
        if productos_sin_stock:
            return productos_sin_stock, None
        # crea el objeto venta
        venta = Sale.objects.create(
            date_sale=timezone.now(),
            count=0,
            amount=0,
            type_invoce=params_venta['type_invoce'],
            type_payment=params_venta['type_payment'],
            descuento=params_venta['descuento'],
            user=params_venta['user'],
            
        )
        #
        ventas_detalle = []
        productos_en_venta = []
        for producto_car in productos_en_car:
            producto = producto_car.product
            
            venta_detalle = SaleDetail(
                product=producto_car.product,
                sale=venta,
                count=producto_car.count,
                
                price_sale=producto_car.product.sale_price,
                tax=0,
            )
            # actualizmos stok de producto en iteracion
            producto = producto_car.product
            producto.count = producto.count - producto_car.count
            producto.num_sale = producto.num_sale + producto_car.count
            #
            ventas_detalle.append(venta_detalle)
            productos_en_venta.append(producto)
            #
            venta.count = venta.count + producto_car.count
            venta.amount = venta.amount + producto_car.count*producto_car.product.sale_price 
            venta.amount = venta.amount 

        venta.amount = venta.amount - venta.descuento
        
        venta.save()
        # Enviar mensaje al bot de Telegram sobre la venta realizada
        tipo_pago = venta.get_type_payment_display()
        productos_nombres = ", ".join([producto.name for producto in productos_en_venta])
        mensaje = (
            f"🎉 *¡Venta Realizada!* {venta.amount} Bs 🎉\n\n"
            f"🛍️ *Detalles de la venta:*\n\n"
            f"    🧾 *Productos:* \n"
        )

        # Añadimos los productos con su cantidad y precio
        for producto in productos_en_venta:
            producto_car = CarShop.objects.get(product=producto, cart__user=params_venta['user'], cart__is_active=True)
            mensaje += f" - {producto.name} (Cantidad: {producto_car.count}) 🏷️ {producto_car.product.sale_price} Bs\n"

       
        # El mensaje final
        mensaje += (
            f"\n💳 *Tipo de pago:* {tipo_pago}\n"
            f"💸 *Descuento aplicado:* {params_venta['descuento']} BS\n\n"
            
        )

        # Enviar mensaje al bot de Telegram (asumiendo que ya tienes el chat_id del bot)
        send_telegram_message(mensaje)
        SaleDetail.objects.bulk_create(ventas_detalle)
        # actualizamos el stok
        Producto.objects.bulk_update(productos_en_venta, ['count', 'num_sale'])
        # completada la venta, eliminamos productos delc arrito
        productos_en_car.delete()
        return productos_sin_stock, venta
    else:
        return productos_sin_stock, None
    
def send_telegram_message(message: str):
    token = '7651415123:AAG8VwRGEJbtxfOgYeq7h3XmR8hEO8mcbVk'
    chat_id = '754834732'  # Este debe ser el ID del chat o grupo al que deseas enviar el mensaje
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown' 
    }
    response = requests.post(url, data=data)
    return response