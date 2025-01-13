from django.utils import timezone
from django.db.models import Prefetch
#from datetime import datetime
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from django.shortcuts import get_object_or_404
import os
import io
import qrcode
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import logging
from applications.productos.models import Producto
from .models import CarShopPed, CartP, Pedido, PedidoDetail
import requests
def procesar_pedido(self, **params_venta):
    # Recupera la lista de productos en el carrito
    productos_en_car = CarShopPed.objects.filter(cart__user=params_venta['user'], cart__is_active=True)
    
    # Verificamos si hay productos en el carrito
    if productos_en_car.count() > 0:
        # Convertimos las fechas en los parámetros a objetos datetime si son válidas
        #fecha_inicio = params_venta.get('fecha_inicio')
        fecha_entrega = params_venta.get('fecha_entrega')
        # Calcular el saldo (si es necesario)
        adelanto = params_venta.get('adelanto', 0)
        if adelanto is None or adelanto == '':
            adelanto = 0
        descuento = params_venta.get('descuento', 0)
        if descuento is None or descuento == '':
            descuento = 0

        # Crear el objeto pedido
        pedido = Pedido.objects.create(
            date_sale=timezone.now(),
            date_entrega=fecha_entrega,
            count=0,
            amount=0,
            type_invoce=params_venta['type_invoce'],
            type_payment=params_venta['type_payment'],
            descuento=descuento,
            user=params_venta['user'],
            type_entrega = params_venta['tipo_entrega'],
            # Campos adicionales
            cliente_nombre=params_venta.get('cliente_nombre'),
            cliente_celular=params_venta.get('cliente_celular'),
            cliente_carnet=params_venta.get('carnet'),
            adelanto=adelanto,
            saldo=0,  # Inicializamos saldo en 0
            cliente_departamento=params_venta.get('departamento'),
            cliente_direccion=params_venta.get('direccion'),
            cliente_sucursal=params_venta.get('sucursal'),
            description=params_venta.get('description')
        )
        
        pedidos_detalle = []
        
        # Crear detalles de pedido primero, sin extras
        for producto_car in productos_en_car:
            producto = producto_car.product
            producto_precio_total = producto_car.product.sale_price

            # Sumar el precio de los extras al precio del producto
            for extra in producto_car.extras.all():
                producto_precio_total += extra.price  # Asumimos que 'price' es el precio de cada extra

            # Crear el objeto PedidoDetail
            pedido_detalle = PedidoDetail(
                product=producto_car.product,
                pedido=pedido,
                count=producto_car.count,
                price_sale=producto_precio_total,  # Usamos el precio total con extras
                tax=0,  # Suponiendo que no hay impuesto para simplificar
            )
            
            # Añadir el detalle al listado
            pedidos_detalle.append(pedido_detalle)
            
            # Actualizamos los totales del pedido, considerando el precio total con extras
            pedido.count += producto_car.count
            pedido.amount += producto_car.count * producto_precio_total 
        
        # Guardar el pedido
        pedido.save()
        
        # Crear detalles de venta en bulk
        PedidoDetail.objects.bulk_create(pedidos_detalle)

        # Asignar los extras a los detalles de pedido ya guardados
        for i, producto_car in enumerate(productos_en_car):
            pedido_detalle = pedidos_detalle[i]  # Recuperar el PedidoDetail correspondiente
            pedido_detalle.extras.set(producto_car.extras.all())  # Asignar los extras
            pedido_detalle.save()  # Guardar las relaciones ManyToMany

        # Aplica descuento sobre el monto total con los extras ya incluidos
        pedido.amount -= descuento
        
        # Calcula el saldo (el saldo es la diferencia entre el total y el adelanto)
        pedido.saldo = pedido.amount - adelanto

        # Actualizamos el pedido con el saldo final
        pedido.save()

        # Eliminamos los productos del carrito
        productos_en_car.delete()
        
        return pedido
    else:
        return None



def generate_qr_code2(order_id):
    try:
        # 34Crear los datos del QR (esto depende de cómo quieras estructurarlos)
        qr_data = f"PE=id:{order_id}"
        
        # Configurar el QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")
        
        # Crear un archivo en memoria
        qr_bio = io.BytesIO()
        qr_img.save(qr_bio, format="PNG")
        qr_bio.seek(0)
        
        # Crear una ruta para el archivo dentro de la carpeta 'qr_ped' en 'media'
        qr_filename = f"qr_pedido.png"  # El nombre del archivo puede incluir el order_id
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_ped')  # Carpeta para los códigos QR
        
        # Crear la carpeta si no existe
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
        
        qr_filepath = os.path.join(qr_dir, qr_filename)
        
        # Guardar el archivo en la carpeta media/qr_ped
        with open(qr_filepath, "wb") as qr_file:
            qr_file.write(qr_bio.getvalue())
        
        return qr_filepath
    except Exception as e:
        logging.error(f"Error generating QR code: {e}")
        return None


def print_ticket(venta):
    try:
        # Acceder a los atributos del modelo de Django (venta es una instancia de Pedido)
        nombre_cliente = venta.cliente_nombre.upper()
        celular_cliente = venta.cliente_celular
        descuento = venta.descuento
        adelanto = venta.adelanto
        saldo = venta.saldo
        fecha_inicio = venta.date_sale
        fecha_entrega = venta.date_entrega
        tipo_entrega = venta.get_type_entrega_display()
        departamento = venta.cliente_departamento
        direccion = venta.cliente_direccion
        amount = venta.amount
        description = venta.description
        carnet = venta.cliente_carnet
        sucursal = venta.cliente_sucursal
        
        
        # Suponemos que tienes una función que obtiene los productos del pedido
        productos_str = obtener_productos_del_pedido(venta) # Función de ejemplo para obtener productos"
        
        # Generar QR para el pedido (aquí se puede usar la lógica del QR)
        order_id = venta.id  # Aquí usamos el ID de la venta
        qr_filepath = generate_qr_code2(order_id)
        qr_img = Image.open(qr_filepath).resize((220, 220))

        # WhatsApp QR code
        qr_phone_url = f"https://wa.me/+591{celular_cliente}"
        qr_phone = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr_phone.add_data(qr_phone_url)
        qr_phone.make(fit=True)
        qr_phone_img = qr_phone.make_image(fill="black", back_color="white")
        
        ticket_content = f"""
        Precio Total: {amount} Bs
        Adelanto: {adelanto} Bs
        Fecha de Entrega: {fecha_entrega}
        Método de Entrega: {tipo_entrega}
        """
        
        if tipo_entrega == "Envio":
            ticket_content += f"""
            Departamento: {departamento}
            Dirección: {direccion}
            Carnet: {carnet}
            Sucursal: {sucursal}
            """
        elif tipo_entrega == "Delivery":
            ticket_content += f"""
            Dirección Delivery: {direccion}
            """
        ticket_content += "\n------------------------------"

        # Crear la imagen del ticket
        dpi = 300
        image_width_cm = 7
        image_width_pixels = int((image_width_cm / 2.54) * dpi)
        image_height_pixels = 1200

        ticket_img = Image.new('RGB', (image_width_pixels, image_height_pixels), color='white')
        draw = ImageDraw.Draw(ticket_img)

        # Logo
        logo_path = "media/img/logo2.png"
        logo = Image.open(logo_path).resize((int(image_width_pixels * 0.5), int(image_width_pixels * 0.2)))
        ticket_img.paste(logo, (int(image_width_pixels * 0.05), 10))
        
        # Order QR code
        ticket_img.paste(qr_img, (image_width_pixels - int(image_width_pixels * 0.3), 10))

        # WhatsApp QR code
        qr_phone_img = qr_phone_img.resize((150, 150))

         # Information column
        font_bold_large = ImageFont.truetype("arial.ttf", 40)
        font_regular_small = ImageFont.truetype("arial.ttf", 30)
        font_bold_labels = ImageFont.truetype("arialbd.ttf", 36, index=0, encoding='unic')
        font_regular_data = ImageFont.truetype("arial.ttf", 36, index=0, encoding='unic')

        current_y = int(image_width_pixels * 0.2)
        margin = int(image_width_pixels * 0.05)

        def draw_multiline_text(draw, text, position, font, max_width):
            lines = []
            words = text.split()
            while words:
                line = ''
                while words and draw.textbbox((0, 0), line + ' ' + words[0], font=font)[2] <= max_width:
                    line = ' '.join([line, words.pop(0)]).strip()
                lines.append(line)
            y = position[1]
            for line in lines:
                draw.text((position[0], y), line, font=font, fill="black")
                y += font.getbbox(line)[3] + 5
            return y
        
        # Información del cliente
        draw.text((margin, current_y), "Nombre del Cliente:", font=font_bold_labels, fill="black")
        current_y += 40
        
        current_y = draw_multiline_text(draw, nombre_cliente, (margin, current_y), font_regular_data, image_width_pixels - margin * 2 - int(image_width_pixels * 0.3))
        print("--------1")
        current_y += 25
        
        draw.text((margin, current_y), "Celular:", font=font_bold_labels, fill="black")
        current_y += 40
        draw.text((margin, current_y), celular_cliente, font=font_regular_data, fill="black")
        current_y += 40
        
        draw.text((margin, current_y), "------------------------------", font=font_regular_small, fill="black")
        current_y += 40
         
        draw.text((margin, current_y), "Productos:", font=font_regular_small, fill="black")
        current_y += 30
           
        # Productos en el ticket
        for producto in productos_str.split('\n'):
            draw.text((margin, current_y), producto, font=font_regular_small, fill="black")
            current_y += 30
          
        draw.text((margin, current_y), "------------------------------", font=font_regular_small, fill="black")
        current_y += 40
        
        # Información adicional
        for line in ticket_content.strip().split('\n'):
            draw.text((margin, current_y), line.strip(), font=font_regular_small, fill="black")
            current_y += 30

        current_y += 15
        
        # Agregar balance
        if saldo == 0:
            balance_label_text = "CANCELADO:"
            balance_text = ""
        else:
            balance_label_text = "Saldo:"
            balance_text = f"{saldo} Bs"
        balance_font_label = ImageFont.truetype("arialbd.ttf", 48, index=0, encoding='unic')
        balance_font_data = ImageFont.truetype("arial.ttf", 48, index=0, encoding='unic')

        qr_whatsapp_x = int(image_width_pixels * 0.7) + 20
        qr_whatsapp_y = current_y - 100

        whatsapp_text = "WhatsApp"
        whatsapp_font = ImageFont.truetype("arial.ttf", 28, index=0, encoding='unic')
        whatsapp_text_width, whatsapp_text_height = draw.textbbox((0, 0), whatsapp_text, font=whatsapp_font)[2:]
        whatsapp_text_x = qr_whatsapp_x + (qr_phone_img.width - whatsapp_text_width) // 2
        whatsapp_text_y = qr_whatsapp_y + qr_phone_img.height + 5

        draw.text((whatsapp_text_x, whatsapp_text_y), whatsapp_text, font=whatsapp_font, fill="black")
        ticket_img.paste(qr_phone_img, (qr_whatsapp_x, qr_whatsapp_y))

        draw.text((margin, current_y), balance_label_text, font=balance_font_label, fill="black")
        draw.text((margin + 150, current_y), balance_text, font=balance_font_data, fill="black")
           
         # Guardar la imagen en la carpeta 'media/tickets_ped/'
        ticket_directory = os.path.join(settings.MEDIA_ROOT, 'tickets_ped')
        if not os.path.exists(ticket_directory):
            os.makedirs(ticket_directory)

        # Define el nombre del archivo de la imagen (por ejemplo, usando el ID del pedido)
        ticket_filename = f"ticket_temp.png"
        ticket_filepath = os.path.join(ticket_directory, ticket_filename)

        # Guardar la imagen
        ticket_img.save(ticket_filepath, dpi=(300, 300))
        
        return f"/media/tickets_ped/{ticket_filename}" 

    except Exception as e:
        logging.error(f"Error en print_ticket: {e}")
        return None
    
def obtener_productos_del_pedido(venta):
    # Obtener todos los detalles de los productos asociados al pedido
    productos = PedidoDetail.objects.filter(pedido=venta, anulate=False)
    
    # Crear una lista con los productos formateados
    productos_str = []
    
    for detalle in productos:
        producto = detalle.product.name  # Nombre del producto
        cantidad = detalle.count  # Cantidad del producto
        precio_venta = detalle.price_sale  # Precio de venta
        
        # Obtener los extras relacionados con el producto
        extras = detalle.extras.all()  # Relación Many-to-Many con los extras
        
        # Crear el acrónimo de los extras
        extras_acronyms = ' '.join([get_acronym(extra.name) for extra in extras])
        
        # Formatear el producto con su cantidad, precio y extras
        productos_str.append(f"{producto} x{cantidad} - {precio_venta} Bs ({extras_acronyms})")
    
    # Unir todos los productos en una sola cadena con saltos de línea
    return "\n".join(productos_str)
def get_acronym(text):
    """Obtiene las iniciales de las palabras de un texto."""
    return ''.join([word[0].upper() for word in text.split()])


def print_ticket_envio(venta):
    try:
        # Acceder a los atributos del modelo de Django (venta es una instancia de Pedido)
        nombre_cliente = venta.cliente_nombre.upper()
        celular_cliente = venta.cliente_celular
        
        departamento = venta.cliente_departamento.upper()
        direccion = venta.cliente_direccion.upper()
        
        carnet = venta.cliente_carnet.upper()
        sucursal = venta.cliente_sucursal.upper()

        # Cargar la imagen base
        base_image_path = "media/img/ticket.jpg"
        base_image = Image.open(base_image_path)
        base_width, base_height = base_image.size

        # Crear una imagen temporal para calcular el tamaño del texto
        temp_image = Image.new('RGBA', (1000, 1000), (255, 255, 255, 0))
        draw = ImageDraw.Draw(temp_image)

        # Fuentes
        font_path = "arial.ttf"
        font_size_name = 80
        font_size_info = 60
        font_size_city = 90
        font_size_address = 60

        font_name = ImageFont.truetype(font_path, font_size_name)
        font_info = ImageFont.truetype(font_path, font_size_info)
        font_city = ImageFont.truetype(font_path, font_size_city)
        font_address = ImageFont.truetype(font_path, font_size_address)

        # Lógica para dividir el nombre si tiene más de dos elementos
        name_parts = nombre_cliente.split()
        if len(name_parts) > 2:
            nombre_cliente = ' '.join(name_parts[:2]) + "\n" + ' '.join(name_parts[2:])

        # Función para centrar el texto y calcular el tamaño de la imagen necesaria
        def calculate_text_size(draw, text, font, line_spacing=3):
            lines = text.split('\n')
            max_text_width = 0
            total_text_height = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                max_text_width = max(max_text_width, text_width)
                total_text_height += text_height + line_spacing
            return max_text_width, total_text_height

        # Calcular el tamaño del texto
        max_width_name, height_name = calculate_text_size(draw, nombre_cliente, font_name, line_spacing=3)
        max_width_carnet, height_carnet = calculate_text_size(draw, f"C.I.: {carnet}", font_info, line_spacing=3)
        max_width_phone, height_phone = calculate_text_size(draw, f"CEL.: {celular_cliente}", font_info, line_spacing=3)
        max_width_department, height_department = calculate_text_size(draw, departamento, font_city, line_spacing=3)
        max_width_address, height_address = calculate_text_size(draw, f"{sucursal}", font_address, line_spacing=3)

        # Calcular el tamaño final de la imagen de texto
        final_text_width = max(max_width_name, max_width_carnet, max_width_phone, max_width_department, max_width_address) + 20
        final_text_height = height_name + height_carnet + height_phone + height_department + height_address + int(0.8 * temp_image.height / 100) + 30

        # Crear la imagen de texto final con el tamaño adecuado
        text_image = Image.new('RGBA', (final_text_width, final_text_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_image)

        # Función para centrar el texto y dibujarlo
        def draw_centered_text(draw, text, font, y, max_width, line_spacing=3, bold=False):
            lines = text.split('\n')
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (max_width - text_width) // 2
                if bold:
                    draw.text((x, y), line, font=font, fill="black", stroke_width=1, stroke_fill="black")
                else:
                    draw.text((x, y), line, font=font, fill="black")
                y += text_height + line_spacing
            return y

        # Dibujar el texto en la imagen de texto final
        current_y = 0
        current_y = draw_centered_text(draw, nombre_cliente, font_name, current_y, final_text_width, line_spacing=5, bold=True)
        current_y += int(0.4 * text_image.height / 100)
        current_y = draw_centered_text(draw, f"C.I.: {carnet}", font_info, current_y, final_text_width, line_spacing=5)
        current_y += int(0.1 * text_image.height / 100)
        current_y = draw_centered_text(draw, f"CEL.: {celular_cliente}", font_info, current_y, final_text_width, line_spacing=5)
        current_y += int(0.5 * text_image.height / 100)
        current_y = draw_centered_text(draw, departamento, font_city, current_y, final_text_width, line_spacing=5, bold=True)
        current_y += int(2 * text_image.height / 100)
        draw_centered_text(draw, f"{sucursal}", font_address, current_y, final_text_width, line_spacing=5, bold=True)
        

        # Crear el directorio para guardar la imagen en MEDIA_ROOT (si no existe)
        ticket_dir = os.path.join(settings.MEDIA_ROOT, 'tickets_ped')
        os.makedirs(ticket_dir, exist_ok=True)

        # Guardar la imagen de texto
        ticket_image_path = os.path.join(ticket_dir, f"ticket_pedidoID.png")
        text_image.save(ticket_image_path)

        # Cargar la imagen de texto y redimensionarla para ajustarla al área de los márgenes
        text_image = Image.open(ticket_image_path)
        margin_x = 150
        margin_y = 10
        margin_width = 670
        margin_height = 485
        text_image_resized = text_image.resize((margin_width, margin_height), Image.LANCZOS)

        # Dibujar un margen azul en la imagen base para la posición donde se pegará el texto
        draw_base = ImageDraw.Draw(base_image)
        draw_base.rectangle([margin_x, margin_y, margin_x + margin_width, margin_y + margin_height], outline="blue", width=3)

        # Pegar la imagen de texto redimensionada sobre la imagen base
        base_image.paste(text_image_resized, (margin_x, margin_y), text_image_resized)

        # Generar el código QR
        qr_url = f"https://wa.me/+591{celular_cliente}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        # Convertir el código QR a un formato de imagen compatible
        qr_img_io = io.BytesIO()
        qr_img.save(qr_img_io, format="PNG")
        qr_img_io.seek(0)
        qr_img = Image.open(qr_img_io)

        # Redimensionar el código QR para que encaje en la esquina inferior izquierda
        qr_size_px = int(2.5 * 120 / 2.54)
        qr_img = qr_img.resize((qr_size_px, qr_size_px), Image.LANCZOS)

        # Pegar el código QR en la esquina inferior izquierda
        qr_x = 10
        qr_y = base_height - qr_size_px - 10
        base_image.paste(qr_img, (qr_x, qr_y))

        # Rotar la imagen combinada 90 grados
        rotated_image = base_image.rotate(90, expand=True)

        # Ajustar el tamaño de la imagen a 7 cm de ancho con una resolución de 300 ppi
        target_width_cm = 7
        target_dpi = 300
        target_width_px = int(target_width_cm / 2.54 * target_dpi)
        aspect_ratio = rotated_image.height / rotated_image.width
        target_height_px = int(target_width_px * aspect_ratio)

        resized_image = rotated_image.resize((target_width_px, target_height_px), Image.LANCZOS)

        # Guardar la imagen combinada rotada y redimensionada
        combined_image_path = os.path.join(ticket_dir, f"combined_ticket.png")
        resized_image.save(combined_image_path, dpi=(300, 300))

        # Retornar la ruta relativa de la imagen para el cliente
        return f"/media/tickets_ped/combined_ticket.png"

    except Exception as e:
        logging.error(f"Error in print_ticket: {e}")
        return None
    

##Enviar el formulario de update del pedido
def editar_pedido(self, **params_venta):
    # Recuperar el ID del pedido que se quiere editar
    pedido_id = params_venta.get('pedido_id')
    
    # Verificar si el ID del pedido es válido
    if not pedido_id:
        raise ValueError("No se ha proporcionado un ID de pedido para editar.")
    
    productos_en_car = CarShopPed.objects.filter(cart__user=params_venta['user'], cart__is_active=True)
    


    # Obtener el pedido existente usando el ID
    pedido = get_object_or_404(Pedido, id=pedido_id)
    

    
    # Convertir las fechas en los parámetros a objetos datetime si son válidas
    fecha_inicio = params_venta.get('fecha_inicio')
    fecha_entrega = params_venta.get('fecha_entrega')
    adelanto = params_venta.get('adelanto', 0)
    descuento = params_venta.get('descuento', 0)
    
    if adelanto is None or adelanto == '':
            adelanto = 0
        
    if descuento is None or descuento == '':
        descuento = 0
    # Actualizar los campos del pedido con los datos del formulario
    
    pedido.date_entrega = fecha_entrega
    pedido.type_payment = params_venta['type_payment']
    pedido.type_entrega = params_venta['tipo_entrega']
    pedido.cliente_nombre = params_venta.get('cliente_nombre')
    pedido.cliente_celular = params_venta.get('cliente_celular')
    pedido.cliente_carnet = params_venta.get('carnet')
    pedido.adelanto = adelanto
    pedido.saldo = 0  # Se reasigna el saldo como 0 para que se calcule con el descuento
    pedido.amount = 0
    pedido.count = 0
    pedido.descuento=descuento
    pedido.cliente_departamento = params_venta.get('departamento')
    pedido.cliente_direccion = params_venta.get('direccion')
    pedido.cliente_sucursal = params_venta.get('sucursal')
    pedido.description = params_venta.get('description')
    pedido.entregado = params_venta.get('entregado')
    
    # Guardar el pedido con los cambios
    pedido.save()
    
     # Obtener el carrito activo del usuario
    carrito_usuario = CartP.objects.filter(user=params_venta['user'], productos_cargados=True).first()
    
    # Si no existe un carrito activo para el usuario, mostrar error
    if not carrito_usuario:
        print("no existe un carrito activo para el usuario, mostrar error")
        return None  # O lanzar un mensaje de error si prefieres
    
    # Obtener los productos en el carrito del usuario
    productos_en_car = CarShopPed.objects.filter(cart=carrito_usuario)
    
    # Eliminar los productos anteriores en el PedidoDetail (detalles del pedido)
    PedidoDetail.objects.filter(pedido=pedido).delete()
    
    # Crear una lista de los productos en el carrito de compra para agregarlos al pedido
    pedidos_detalle = []
    
    # Crear los detalles de pedido (productos) con los datos actualizados
    for producto_car in productos_en_car:
        producto = producto_car.product
        producto_precio_total = producto_car.product.sale_price

        # Sumar el precio de los extras al precio del producto
        for extra in producto_car.extras.all():
            producto_precio_total += extra.price

        # Crear el objeto PedidoDetail
        pedido_detalle = PedidoDetail(
            product=producto_car.product,
            pedido=pedido,
            count=producto_car.count,
            price_sale=producto_precio_total,  # Usar el precio total con extras
            tax=0,  # Suponiendo que no hay impuestos
        )
        
        pedidos_detalle.append(pedido_detalle)
        
        # Actualizar los totales del pedido
        pedido.count += producto_car.count
        pedido.amount += producto_car.count * producto_precio_total
    
    
    # Guardar los detalles del pedido
    PedidoDetail.objects.bulk_create(pedidos_detalle)

    # Asignar los extras a los detalles de pedido ya guardados
    for i, producto_car in enumerate(productos_en_car):
        pedido_detalle = pedidos_detalle[i]  # PedidoDetail correspondiente
        pedido_detalle.extras.set(producto_car.extras.all())  # Asignamos los extras
        pedido_detalle.save()  # Guardamos las relaciones ManyToMany

    # Aplicar descuento sobre el monto total
    pedido.amount -= descuento
    
    # Calcular el saldo
    pedido.saldo = pedido.amount - adelanto
    pedido.save()

    # Eliminar los productos del carrito después de procesar el pedido
    productos_en_car.delete()
    
    # Ahora, actualizamos el carrito del usuario a inactivo
    carrito_usuario.is_active = True
    carrito_usuario.productos_cargados = False
    carrito_usuario.save()  # Guardar el carrito con is_active=False
    
    return pedido





#TELEGRAM BOT
def send_telegram_message(message: str):
    token = '7651415123:AAG8VwRGEJbtxfOgYeq7h3XmR8hEO8mcbVk'
    chat_id = '754834732'  # Este debe ser el ID del chat o grupo al que deseas enviar el mensaje
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=data)
    return response

def send_telegram_photo(photo_path: str):
    """
    Enviar una foto a un chat de Telegram.
    
    :param photo_path: La ruta de la imagen que deseas enviar.
    """
    token = '7651415123:AAG8VwRGEJbtxfOgYeq7h3XmR8hEO8mcbVk'
    chat_id = '754834732'  # Este debe ser el ID del chat o grupo al que deseas enviar la foto
    url = f'https://api.telegram.org/bot{token}/sendPhoto'
    
    # Abrir la imagen y enviarla
    with open(photo_path, 'rb') as photo_file:
        photo_data = {
            'chat_id': chat_id,
        }
        files = {
            'photo': photo_file
        }
        # Realizar la solicitud POST para enviar la foto
        response = requests.post(url, data=photo_data, files=files)
    
    return response  # Regresar la respuesta de la solicitud