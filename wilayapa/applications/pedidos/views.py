from django.shortcuts import render,redirect
from django.views.generic.edit import (
    FormView
)
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    View,
    UpdateView,
    DeleteView,
    DeleteView,
    DetailView,
    ListView
)
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse

from .forms import PedidoDatosForm,PedidoForm,ScanneQRForm,VentaVoucherForm
from .models import CarShopPed,CartP,Pedido,PedidoDetail
from applications.productos.models import Producto, Extra
import json
from django.core.serializers.json import DjangoJSONEncoder
from .functions import procesar_pedido, print_ticket,generate_qr_code2, print_ticket_envio,editar_pedido,send_telegram_message
import os
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from applications.users.mixins import AdminPermisoMixin,VentasPermisoMixin

import threading
# Create your views here.
class AddCarPedView(AdminPermisoMixin,FormView):
    template_name = 'pedidos/new_pedido.html'
    form_class = PedidoForm
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = CartP.objects.get_or_create(user=self.request.user, is_active=True)
        context["productos"] = CarShopPed.objects.filter(cart=cart).order_by('-created')
        context["total_cobrar"] = CarShopPed.objects.total_cobrar(self.request.user)
        # Pasamos los QR al contexto
        image_path = os.path.join(settings.MEDIA_ROOT, 'tickets_ped/ticket_temp.png')
        context['combined_image'] = '/media/tickets_ped/ticket_temp.png' if os.path.exists(image_path) else None
        image_path2 = os.path.join(settings.MEDIA_ROOT, 'tickets_ped/combined_ticket.png')
        context['combined_image_envio'] = '/media/tickets_ped/combined_ticket.png' if os.path.exists(image_path2) else None
        context['datos_ped'] = PedidoDatosForm
        
        productos_con_extras = {}
        for producto in Producto.objects.all():
            productos_con_extras[producto.id] = [
                {'id': extra.id, 'name': extra.name, 'price': float(extra.price)} 
                for extra in producto.extra.all()
            ]
        
        context['productos_con_extras'] = json.dumps(productos_con_extras, cls=DjangoJSONEncoder)
        
        return context
    
    def form_valid(self, form):
        print('Validando formulario')
        productoId = form.cleaned_data['productId']
        count = form.cleaned_data['count']
        
        cart, created = CartP.objects.get_or_create(user=self.request.user, is_active=True)
        
        if productoId:
            producto = Producto.objects.get(id=productoId.id)
            total_extras = 0
            extras = form.cleaned_data.get('extra')
            print(f"Extras seleccionados: {extras}")
            
            # Calcular el precio con extras
            if extras:
                total_extras = sum(extra.price for extra in extras)

            total_precio = producto.sale_price + total_extras
            precio_total = total_precio * count

            # **1. No crear el producto sin extras si estamos añadiendo productos con extras**
            if not extras:
                # Buscar si ya existe el producto sin extras en el carrito
                obj_producto = CarShopPed.objects.filter(
                    barcode=f'{productoId.id}_sin_extras',
                    cart=cart
                ).first()

                if obj_producto:
                    # Si ya existe, actualizamos la cantidad y el precio
                    obj_producto.count += count
                    obj_producto.precio_total += producto.sale_price * count
                    obj_producto.save()
                else:
                    # Si no existe, lo creamos
                    obj_producto = CarShopPed.objects.create(
                        barcode=f'{productoId.id}_sin_extras',
                        cart=cart,
                        product=producto,
                        count=count,
                        precio_total=producto.sale_price * count
                    )
            else:
                # Si se seleccionaron extras, no creamos un producto sin extras
                obj_producto = None

            # **2. Crear o actualizar las combinaciones de extras**
            if extras:
                # Crear una clave única para la combinación de extras seleccionados
                extras_ids = sorted(extra.id for extra in extras)
                extras_key = "_".join(map(str, extras_ids))  # Creamos una clave única por los extras seleccionados

                barcode_combinacion = f'{productoId.id}_{extras_key}'  # Crear un barcode único para la combinación de producto + extras
                
                # Verificar si la combinación de producto + extras ya existe
                obj_combinacion, created = CarShopPed.objects.get_or_create(
                    barcode=barcode_combinacion,  # Barcode único para la combinación
                    cart=cart,
                    defaults={ 
                        'product': producto,
                        'count': count,
                        'precio_total': (producto.sale_price + total_extras) * count
                    }
                )
                if not created:
                    # Si ya existe la combinación, actualizamos la cantidad y el precio
                    obj_combinacion.count += count
                    obj_combinacion.precio_total += (producto.sale_price + total_extras) * count
                    obj_combinacion.save()

                # Asociamos los extras a esta combinación
                obj_combinacion.extras.set(extras)  # Usamos set() para establecer todos los extras seleccionados correctamente

        return super(AddCarPedView, self).form_valid(form)
    def form_invalid(self, form):
        print('Formulario inválido')
        print(form.errors)  # Imprimir los errores del formulario
        return super().form_invalid(form)
    

class CarShopUpdateView(AdminPermisoMixin,View):
    """Quita en 1 la cantidad en un carshop"""

    def post(self, request, *args, **kwargs):
        # Obtenemos el objeto CarShopPed usando el ID proporcionado
        car = CarShopPed.objects.get(id=self.kwargs['pk'])

        # Comprobamos que la cantidad sea mayor que 1 antes de restar
        if car.count > 1:
            car.count -= 1  # Reducimos la cantidad en 1

            # Recalculamos el precio total con la nueva cantidad
            # Sumamos el precio de los extras y multiplicamos por la nueva cantidad
            total_extras = sum(extra.price for extra in car.extras.all())
            total_precio = (car.product.sale_price + total_extras) * car.count

            # Actualizamos el campo precio_total con el nuevo valor calculado
            car.precio_total = total_precio
            car.save()

        return HttpResponseRedirect(
            reverse(
                'pedidos_app:pedido-nuevo'
            ) # Redirigimos a la misma página después de actualizar
        )
class CarShopDeleteView(AdminPermisoMixin,DeleteView):
    model = CarShopPed
    success_url = reverse_lazy('pedidos_app:pedido-nuevo')

class CarShopDeleteAll(AdminPermisoMixin,View):
    
    
    def post(self, request, *args, **kwargs):
        #
        cart = CartP.objects.get(user=request.user, is_active=True)
        
        # Eliminamos solo los productos del carrito seleccionado
        CarShopPed.objects.filter(cart=cart).delete()
        #
        return HttpResponseRedirect(
            reverse(
                'pedidos_app:pedido-nuevo'
            )
        )
    

class ProcesoPedidoGuardarView(AdminPermisoMixin,FormView):
    print("entrando al view form ***************22222************")
    form_class = PedidoDatosForm
    success_url = reverse_lazy('pedidos_app:pedido-lista')
    
   
    
    def form_valid(self, form):
        print("Validando form ***************************")
        # Recoger los valores del formulario
        type_payment = form.cleaned_data['type_payment']
        
        descuento = form.cleaned_data['descuento']
        adelanto = form.cleaned_data['adelanto']
        saldo = form.cleaned_data['saldo']
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_entrega = form.cleaned_data['fecha_entrega']
        tipo_entrega = form.cleaned_data['type_entrega']
        departamento = form.cleaned_data['departamento']
        custom_department = form.cleaned_data['custom_department']
        sucursal = form.cleaned_data['sucursal']
        carnet = form.cleaned_data['carnet']
        nombre_cliente = form.cleaned_data['cliente_nombre']
        celular_cliente = form.cleaned_data['cliente_celular']
        
        # Obtener las direcciones del formulario
        direccion = form.cleaned_data.get('direccion', '')
        direccion2 = form.cleaned_data.get('direccionEnvio', '')
        description = form.cleaned_data.get('description', '')
        # Obtener el ID del pedido a editar
        pedido_id = form.cleaned_data.get('pedido_id')
        
        # Lógica para determinar cuál dirección usar
        if tipo_entrega == '1':
            # Si 'direccion' tiene valor y 'direccionEnvio' está vacía
            direccion_final = direccion2
        elif tipo_entrega == '2':
            # Si 'direccion' tiene valor y 'direccionEnvio' está vacía
            direccion_final = direccion
        else:
            direccion_final = 'sin direccion'
         
        if departamento == 'other':
            departamento = custom_department

        

        # Imprimir para debugging (puedes eliminar después)
        print(f"Descuento: {descuento}, Adelanto: {adelanto}, Saldo: {saldo}")
        print(f"Fecha de inicio: {fecha_inicio}, Fecha de entrega: {fecha_entrega}")
        print(f"Tipo de entrega: {tipo_entrega}, Departamento: {departamento}")
        print(f"Dirección: {direccion_final}")

        # Llamamos a la función editar_pedido
        venta = procesar_pedido(
            self=self,
            pedido_id=pedido_id,
            descuento=descuento,
            adelanto=adelanto,
            saldo=0,
            type_invoce=2,
            carnet=carnet,
            cliente_celular=celular_cliente,
            cliente_nombre=nombre_cliente,
            type_payment=type_payment,
            fecha_inicio=fecha_inicio,
            fecha_entrega=fecha_entrega,
            tipo_entrega=tipo_entrega,
            departamento=departamento,
            custom_department=custom_department,
            direccion=form.cleaned_data['direccion'],
            description=form.cleaned_data['description'],
            sucursal=sucursal,
            user=self.request.user,
        )

        
        if venta is None:
            messages.error(self.request, f"No hay productos en el carrito para realizar el pedido")
            return HttpResponseRedirect(reverse('pedidos_app:pedido-lista'))
        if tipo_entrega == '1':
            print("*************esto es un envio")
            print_ticket_envio(venta)

        print_ticket(venta)
        
        
        # Si todo es correcto, redirigir a una página de éxito
        
        return HttpResponseRedirect(reverse('pedidos_app:pedido-lista'))
    def form_invalid(self, form):
        print('Formulario inválido')
        print(form.errors)  # Imprimir los errores del formulario
        return super().form_invalid(form)
    
class PedidosListView(AdminPermisoMixin,ListView):
    template_name = 'pedidos/lista.html'
    context_object_name = "pedidos" 
    paginate_by = 35
    def validar_fechas(self, fecha_inicio, fecha_fin):
        # Definir la fecha actual
        fecha_actual = datetime.now()

        # Convertir las fechas de inicio y fin a objetos datetime si no son None
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        # Si ambas fechas están presentes
        if fecha_inicio and fecha_fin:
            fecha_1 = fecha_inicio
            fecha_2 = fecha_fin

        # Si solo hay fecha de inicio
        elif fecha_inicio and not fecha_fin:
            fecha_1 = fecha_inicio
            fecha_2 = fecha_actual

        # Si solo hay fecha de fin
        elif not fecha_inicio and fecha_fin:
            # Definir una fecha predeterminada, por ejemplo hace un año
            fecha_1 = fecha_actual - timedelta(days=365)  # Hace un año
            fecha_2 = fecha_fin

        else:
            # Si no hay fechas, retornamos un error o mensaje adecuado
            return None, "No se han proporcionado fechas válidas."
        
        # Asegurarse de que las fechas son válidas y coherentes
        if fecha_1 > fecha_2:
           fecha_2 = fecha_actual + timedelta(days=365)
        
        # Devolvemos las fechas procesadas
        return fecha_1, fecha_2
    def get_queryset(self):
        kword = self.request.GET.get("kword", '')
        
        fecha_1 = self.request.GET.get("fecha1", '')
        fecha_2 = self.request.GET.get("fecha2", '')
        estado = self.request.GET.get("estado", '')
        entrega = self.request.GET.get("entrega", '')
        
        
        
        fecha1, fecha2 = self.validar_fechas(fecha_1,fecha_2)
        print(fecha1 , fecha2)
        if fecha1 and fecha2:
            # Si ambas fechas son válidas, realizar la búsqueda con el rango
            queryset = Pedido.objects.buscar_pedido_entrega(kword, fecha1, fecha2,estado,entrega)
        else:
            # Si no hay fechas válidas, realizar la búsqueda sin fechas
            queryset = Pedido.objects.buscar_pedido(kword,estado,entrega)

        
        return queryset.order_by('-date_sale')
class PedidoAnulateView(AdminPermisoMixin,View):
    """ Anula la venta, pero no la elimina de la BD. Devuelve los productos al stock y
    descuenta del numero de venta de los productos """
    
    def post(self, request, *args, **kwargs):
        pedido = Pedido.objects.get(id = self.kwargs['pk'])
        print("ID de la venta: ", self.kwargs['pk'])
        # No se elimina realmente de la base de datos, solo se coloca como anulado. Por temas de                  auditoria
        pedido.anulate = True
        pedido.save()
        # actualizamos el stok y ventas
        
        return HttpResponseRedirect(
            reverse(
                'pedidos_app:pedido-lista'
            )
        )
class DeleteImageTicketView(AdminPermisoMixin,View):
    success_url = reverse_lazy('pedidos_app:pedido-nuevo')
    def get(self, request, *args, **kwargs):
        # Ruta completa de la imagen
        qr_ticket_path = os.path.join(settings.MEDIA_ROOT, 'tickets_ped/ticket_temp.png')
        qr_ticket_envio_path = os.path.join(settings.MEDIA_ROOT, 'tickets_ped/combined_ticket.png')
        
        if os.path.exists(qr_ticket_path):
            os.remove(qr_ticket_path)
            return JsonResponse({'status': 'success', 'message': 'Imagen eliminada correctamente'})
        elif os.path.exists(qr_ticket_envio_path):
            os.remove(qr_ticket_envio_path)
            return JsonResponse({'status': 'success', 'message': 'Imagen eliminada correctamente'})
        
        else:
            return JsonResponse({'status': 'error', 'message': 'La imagen no existe'})
        
class EliminarImagenesTicketView(AdminPermisoMixin,View):
    def post(self, request, *args, **kwargs):
        # Obtener el nombre de la imagen a eliminar desde el cuerpo de la solicitud
        data = json.loads(request.body)
        image_url = data.get('image')

        # Definir la ruta completa de la imagen a eliminar
        image_path = os.path.join(settings.MEDIA_ROOT, image_url.replace('/media/', ''))

        # Eliminar la imagen si existe
        if os.path.exists(image_path):
            os.remove(image_path)
            return JsonResponse({'status': 'success', 'message': 'Imagen eliminada correctamente.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'La imagen no existe.'})
class VerificarImagenTicketView(AdminPermisoMixin,View):
    def get(self, request, *args, **kwargs):
        # Rutas completas de los archivos que queremos verificar
        qr_ticket_path = os.path.join(settings.MEDIA_ROOT, 'tickets_ped', 'ticket_temp.png')
        qr_ticket_envio_path = os.path.join(settings.MEDIA_ROOT, 'tickets_ped', 'combined_ticket.png')

        # Verificar si los archivos existen individualmente
        response_data = {'status': 'success', 'message': 'Imagen(es) encontrada(s).', 'images': {}}

        if os.path.exists(qr_ticket_path):
            response_data['images']['ticket_temp'] = os.path.join(settings.MEDIA_URL, 'tickets_ped', 'ticket_temp.png')

        if os.path.exists(qr_ticket_envio_path):
            response_data['images']['combined_ticket'] = os.path.join(settings.MEDIA_URL, 'tickets_ped', 'combined_ticket.png')

        # Si no hay ninguna imagen, devolver un error
        if not response_data['images']:
            response_data = {
                'status': 'error',
                'message': 'Faltan ambos archivos de imagen en el directorio tickets_ped.',
            }

        return JsonResponse(response_data)
    
class ProcesoPedidoEditarView(AdminPermisoMixin,FormView):
    template_name = 'pedidos/update.html'
    form_class = PedidoForm
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el id del pedido de la URL
        pedido_id = self.kwargs.get('id')

        # Obtener el pedido correspondiente, o mostrar un error si no se encuentra
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # Cargar los productos asociados al pedido
        productos_guardados = PedidoDetail.objects.filter(pedido=pedido)
        
        # Aquí cargamos los datos del pedido en el contexto del formulario
        context['pedido'] = pedido
        context['productos2'] = productos_guardados  # Agregamos los productos al contexto
        context['datos_ped'] = PedidoDatosForm
        # Lista de opciones válidas para 'departamento'
        DEPARTAMENTO_CHOICES = [
            ('La Paz', 'La Paz'),
            ('Cochabamba', 'Cochabamba'),
            ('Santa Cruz', 'Santa Cruz'),
            ('Oruro', 'Oruro'),
            ('Pando', 'Pando'),
            ('Potosí', 'Potosí'),
            ('Tarija', 'Tarija'),
            ('Beni', 'Beni'),
            ('Sucre', 'Sucre'),
            ('Chuquisaca', 'Chuquisaca'),
            ('Colchani', 'Colchani'),
            ('other', 'Otro...'),
        ]
        # Verificamos si el valor de 'cliente_departamento' está en la lista de opciones
        if pedido.cliente_departamento not in dict(DEPARTAMENTO_CHOICES).keys():
            initial_departamento = 'other'  # Si el valor no está en la lista, asignamos 'other'
            initial_custom_department = pedido.cliente_departamento  # Asignamos el valor a custom_department
        else:
            initial_departamento = pedido.cliente_departamento  # Si está en la lista, lo asignamos tal cual
            initial_custom_department = ''
        # Llenar el formulario con los datos del pedido
        form = PedidoDatosForm(initial={
            'type_payment': pedido.type_payment,
            'descuento': pedido.descuento,
            'adelanto': pedido.adelanto,
            'saldo': pedido.saldo,
            'fecha_inicio': pedido.date_sale,
            'entregado': pedido.entregado,
            'fecha_entrega': pedido.date_entrega,
            'type_entrega': pedido.type_entrega,
            'departamento': initial_departamento,
            'custom_department': initial_custom_department,
            'sucursal': pedido.cliente_sucursal,
            'carnet': pedido.cliente_carnet,
            'cliente_nombre': pedido.cliente_nombre,
            'cliente_celular': pedido.cliente_celular,
            'direccion': pedido.cliente_direccion,
            'direccionEnvio': pedido.cliente_direccion,
            'description': pedido.description,
            
        })
        context['datos_ped'] = form
        context['type_entrega'] = pedido.type_entrega
        # Obtener el carrito del usuario
        cart, created = CartP.objects.get_or_create(user=self.request.user, is_active=True)
         # Verificar si los productos ya han sido cargados en el carrito
        if not cart.productos_cargados:
            # Cargar productos si aún no han sido cargados
            self.cargar_productos_al_carrito(cart, productos_guardados)
            # Marcar que los productos han sido cargados
            cart.productos_cargados = True
            cart.save()


        # Productos en el carrito
        context['productos_cargados'] = cart.productos_cargados
        context["productos"] = CarShopPed.objects.filter(cart=cart).order_by('-created')
        context["total_cobrar"] = CarShopPed.objects.total_cobrar(self.request.user)
        
        

        # Pasamos los QR al contexto
        image_path = os.path.join(settings.MEDIA_ROOT, 'tickets_ped/ticket_temp.png')
        context['combined_image'] = '/media/tickets_ped/ticket_temp.png' if os.path.exists(image_path) else None
        image_path2 = os.path.join(settings.MEDIA_ROOT, 'tickets_ped/combined_ticket.png')
        context['combined_image_envio'] = '/media/tickets_ped/combined_ticket.png' if os.path.exists(image_path2) else None
        
        # En la vista, dentro de get_context_data

        productos_con_extras = {}
        for producto in Producto.objects.all():
            productos_con_extras[producto.id] = [
                {'id': extra.id, 'name': extra.name, 'price': float(extra.price)} 
                for extra in producto.extra.all()
            ]
        
        context['productos_con_extras'] = json.dumps(productos_con_extras, cls=DjangoJSONEncoder)
        
        return context

    def cargar_productos_al_carrito(self, cart, productos_guardados):
        """
        Función que agrega automáticamente los productos de un pedido al carrito del usuario,
        solo si no están ya presentes en el carrito.
        """
        existing_items = {item.barcode: item for item in CarShopPed.objects.filter(cart=cart)}
        objects_to_create = []

        for detalle in productos_guardados:
            producto = detalle.product
            count = detalle.count
            extras = detalle.extras.all()
            total_extras = sum(extra.price for extra in extras)

            total_precio = producto.sale_price + total_extras
            precio_total = total_precio * count

            if not extras:
                barcode = f'{producto.id}_sin_extras'
            else:
                extras_ids = sorted(extra.id for extra in extras)
                extras_key = "_".join(map(str, extras_ids))
                barcode = f'{producto.id}_{extras_key}'

            # Verificar si el producto con el mismo barcode ya existe en el carrito
            obj_producto = existing_items.get(barcode)

            if obj_producto:
                # Si ya existe, actualizamos la cantidad y el precio
                obj_producto.count += count
                obj_producto.precio_total += precio_total
                obj_producto.save()

                # Actualizamos los extras si el producto ya está en el carrito
                obj_producto.extras.set(extras)  # Esto asegura que los extras estén bien relacionados
            else:
                # Si no existe, lo agregamos a la lista para crear en bulk
                obj_producto = CarShopPed(
                    barcode=barcode,
                    cart=cart,
                    product=producto,
                    count=count,
                    precio_total=precio_total
                )
                objects_to_create.append(obj_producto)

        # Insertar todos los productos nuevos al carrito de una vez
        if objects_to_create:
            CarShopPed.objects.bulk_create(objects_to_create)

            # Ahora, asignamos los extras a los productos recién creados
            for obj_producto, detalle in zip(objects_to_create, productos_guardados):
                obj_producto.extras.set(detalle.extras.all())  # Asignamos los extras después de la creación
    
    
    def form_valid(self, form):
        print('Validando formulario')
        productoId = form.cleaned_data['productId']
        count = form.cleaned_data['count']
        
        cart, created = CartP.objects.get_or_create(user=self.request.user, is_active=True)
        
        if productoId:
            producto = Producto.objects.get(id=productoId.id)
            total_extras = 0
            extras = form.cleaned_data.get('extra')
            print(f"Extras seleccionados: {extras}")
            
            # Calcular el precio con extras
            if extras:
                total_extras = sum(extra.price for extra in extras)

            total_precio = producto.sale_price + total_extras
            precio_total = total_precio * count

            # **1. No crear el producto sin extras si estamos añadiendo productos con extras**
            if not extras:
                # Buscar si ya existe el producto sin extras en el carrito
                obj_producto = CarShopPed.objects.filter(
                    barcode=f'{productoId.id}_sin_extras',
                    cart=cart
                ).first()

                if obj_producto:
                    # Si ya existe, actualizamos la cantidad y el precio
                    obj_producto.count += count
                    obj_producto.precio_total += producto.sale_price * count
                    obj_producto.save()
                else:
                    # Si no existe, lo creamos
                    obj_producto = CarShopPed.objects.create(
                        barcode=f'{productoId.id}_sin_extras',
                        cart=cart,
                        product=producto,
                        count=count,
                        precio_total=producto.sale_price * count
                    )
            else:
                # Si se seleccionaron extras, no creamos un producto sin extras
                obj_producto = None

            # **2. Crear o actualizar las combinaciones de extras**
            if extras:
                # Crear una clave única para la combinación de extras seleccionados
                extras_ids = sorted(extra.id for extra in extras)
                extras_key = "_".join(map(str, extras_ids))  # Creamos una clave única por los extras seleccionados

                barcode_combinacion = f'{productoId.id}_{extras_key}'  # Crear un barcode único para la combinación de producto + extras
                
                # Verificar si la combinación de producto + extras ya existe
                obj_combinacion, created = CarShopPed.objects.get_or_create(
                    barcode=barcode_combinacion,  # Barcode único para la combinación
                    cart=cart,
                    defaults={ 
                        'product': producto,
                        'count': count,
                        'precio_total': (producto.sale_price + total_extras) * count
                    }
                )
                if not created:
                    # Si ya existe la combinación, actualizamos la cantidad y el precio
                    obj_combinacion.count += count
                    obj_combinacion.precio_total += (producto.sale_price + total_extras) * count
                    obj_combinacion.save()

                # Asociamos los extras a esta combinación
                obj_combinacion.extras.set(extras)  # Usamos set() para establecer todos los extras seleccionados correctamente

        return super(ProcesoPedidoEditarView, self).form_valid(form)
    def form_invalid(self, form):
        print('Formulario inválido')
        print(form.errors)  # Imprimir los errores del formulario
        return super().form_invalid(form)
    
    
class PedidoGuardarView(AdminPermisoMixin,FormView):
    print("entrando al view form ***************22222************")
    form_class = PedidoDatosForm
    success_url = '.'
    
    
    
    def form_valid(self, form):
        print("Validando form ***************************")
        # Recoger los valores del formulario
        type_payment = form.cleaned_data['type_payment']
        
        descuento = form.cleaned_data['descuento']
        adelanto = form.cleaned_data['adelanto']
        saldo = form.cleaned_data['saldo']
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_entrega = form.cleaned_data['fecha_entrega']
        tipo_entrega = form.cleaned_data['type_entrega']
        departamento = form.cleaned_data['departamento']
        custom_department = form.cleaned_data['custom_department']
        sucursal = form.cleaned_data['sucursal']
        carnet = form.cleaned_data['carnet']
        nombre_cliente = form.cleaned_data['cliente_nombre']
        celular_cliente = form.cleaned_data['cliente_celular']
        entregado = form.cleaned_data.get('entregado','')
        
        # Obtener las direcciones del formulario
        direccion = form.cleaned_data.get('direccion', '')
        direccion2 = form.cleaned_data.get('direccionEnvio', '')
        description = form.cleaned_data.get('description', '')
        print("********tipo direccion")
        print(direccion)
        
        print("********tipo entrega")
        print(tipo_entrega)
        if tipo_entrega == '1':
            direccion_final = direccion2
        elif tipo_entrega == '2':
            direccion_final = direccion
        else:
            direccion_final = 'sin direccion'
         
        if departamento == 'other':
            departamento = custom_department

        print("********tipo entrega")
        print(direccion_final)

        # Imprimir para debugging (puedes eliminar después)
        print(f"Descuento: {descuento}, Adelanto: {adelanto}, Saldo: {saldo}")
        print(f"Fecha de inicio: {fecha_inicio}, Fecha de entrega: {fecha_entrega}")
        print(f"Tipo de entrega: {tipo_entrega}, Departamento: {departamento}")
        print(f"Dirección: {direccion}")
        # Capturar el ID del pedido desde la URL (si se pasa en la URL)
        pedido_id = self.kwargs.get('id')
        print(pedido_id)
        if not pedido_id:
            messages.error(self.request, "No se ha proporcionado un ID de pedido para editar.")
            return HttpResponseRedirect(reverse('pedidos_app:pedido-lista'))

        # Obtener el pedido a editar (esto es importante para la actualización)
        pedido = get_object_or_404(Pedido, id=pedido_id)
        # Procesar el pedido con los datos obtenidos
        venta = editar_pedido(
            self=self,
            pedido_id=pedido_id, 
            descuento=descuento,
            adelanto=adelanto,
            saldo=saldo,
            type_invoce=2,
            carnet = carnet,
            cliente_celular=celular_cliente,
            cliente_nombre=nombre_cliente,
            type_payment=type_payment,
            entregado = entregado,
            fecha_entrega=fecha_entrega,
            tipo_entrega=tipo_entrega,
            departamento=departamento,
            
            direccion=direccion_final,
            description=description,
            sucursal=sucursal,
            user=self.request.user,
        )

        
        if venta is None:
            messages.error(self.request, f"No hay productos en el carrito para realizar el pedido")
            return HttpResponseRedirect(reverse('pedidos_app:pedido-nuevo'))
        if tipo_entrega == '1':
            print("*************esto es un envio")
            print_ticket_envio(venta)

        print_ticket(venta)
        """
        thread = threading.Thread(target=self.generar_tickets, args=(venta,tipo_entrega))
        print()
        thread.start()  # Inicia el hilo
        """
        # Si todo es correcto, redirigir a una página de éxito
        
        return HttpResponseRedirect(reverse('pedidos_app:pedido-lista'))
    def generar_tickets(self, venta,tipo_entrega):
        if tipo_entrega == '1':
            print("*************esto es un envio")
            print_ticket_envio(venta)

        print_ticket(venta)
        
    def form_invalid(self, form):
        print('Formulario inválido')
        print(form.errors)  # Imprimir los errores del formulario
        return super().form_invalid(form)
    
class EditCarShopUpdateView(AdminPermisoMixin,View):
    """Quita en 1 la cantidad en un carshop"""

    def post(self, request, *args, **kwargs):
        # Obtenemos el objeto CarShopPed usando el ID proporcionado
        car = CarShopPed.objects.get(id=self.kwargs['pk'])

        # Comprobamos que la cantidad sea mayor que 1 antes de restar
        if car.count > 1:
            car.count -= 1  # Reducimos la cantidad en 1

            # Recalculamos el precio total con la nueva cantidad
            # Sumamos el precio de los extras y multiplicamos por la nueva cantidad
            total_extras = sum(extra.price for extra in car.extras.all())
            total_precio = (car.product.sale_price + total_extras) * car.count

            # Actualizamos el campo precio_total con el nuevo valor calculado
            car.precio_total = total_precio
            car.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
class EditCarShopDeleteView(AdminPermisoMixin,DeleteView):
    model = CarShopPed

    def get_success_url(self):
        # Intentamos obtener la URL de la página anterior
        referer_url = self.request.META.get('HTTP_REFERER', None)
        
        if referer_url:
            # Si existe la URL referida, la devolvemos tal cual
            return referer_url
class EditCarShopDeleteAll(AdminPermisoMixin,View):
    
    
    
    def post(self, request, *args, **kwargs):
        #
        cart = CartP.objects.get(user=request.user, is_active=True)
        
        # Eliminamos solo los productos del carrito seleccionado
        CarShopPed.objects.filter(cart=cart).delete()
        #
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



class DetallePedidoView(AdminPermisoMixin,DetailView):
    model = Pedido  # El modelo que estamos mostrando
    template_name = 'pedidos/detalle.html'  # El template donde se renderiza el detalle
    context_object_name = 'pedido'  # Usamos 'pedido' para el contexto

    def get_context_data(self, **kwargs):
        # Obtenemos el contexto base
        context = super().get_context_data(**kwargs)

        # Obtiene el objeto de 'Pedido' usando el 'id' automáticamente
        pedido = self.get_object()
        
        # Cargar los productos asociados al pedido
        productos_guardados = PedidoDetail.objects.filter(pedido=pedido)
        # Calculamos el precio total para cada PedidoDetail
        for producto in productos_guardados:
            producto.precio_total = producto.price_sale * producto.count
            
        # Lista de departamentos
        DEPARTAMENTO_CHOICES = [
            ('La Paz', 'La Paz'),
            ('Cochabamba', 'Cochabamba'),
            ('Santa Cruz', 'Santa Cruz'),
            ('Oruro', 'Oruro'),
            ('Pando', 'Pando'),
            ('Potosí', 'Potosí'),
            ('Tarija', 'Tarija'),
            ('Beni', 'Beni'),
            ('Sucre', 'Sucre'),
            ('Chuquisaca', 'Chuquisaca'),
            ('Colchani', 'Colchani'),
            ('other', 'Otro...'),
        ]
        
        # Verificamos si el 'cliente_departamento' no está en la lista de opciones
        if pedido.cliente_departamento not in dict(DEPARTAMENTO_CHOICES).keys():
            initial_departamento = 'other'  # Si no está en la lista, asignamos 'other'
            initial_custom_department = pedido.cliente_departamento  # Asignamos el valor a custom_department
        else:
            initial_departamento = pedido.cliente_departamento  # Si está en la lista, lo asignamos tal cual
            initial_custom_department = ''
        
        # Agregar al contexto
        context['productos_guardados'] = productos_guardados
        context['initial_departamento'] = initial_departamento
        context['initial_custom_department'] = initial_custom_department
        

        return context
    

class entregaPedidoView(VentasPermisoMixin,FormView):
    template_name = 'pedidos/entregar.html'  # Usamos un template para mostrar tanto el formulario de escaneo como el de pago
    form_class = ScanneQRForm  # Formulario para escanear o ingresar el ID del pedido
    success_url = '.'  # No es necesario redirigir, la vista recarga con los datos actualizados

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_voucher'] = VentaVoucherForm()  # Formulario de pago que se mostrará si el pedido es válido

        # Verificamos si el pedido se ha cargado en el formulario
        if hasattr(self, 'pedido') and self.pedido:
            context['pedido'] = self.pedido
        else:
            context['pedido'] = None

        return context
    
    def form_valid(self, form):
        # Validamos el formulario de escaneo
        scaneado = form.cleaned_data['id_prod']
        
        try:
            pedidoId = int(scaneado.replace("PE=id:", "").strip())  # Asignamos el ID correcto
        except ValueError:
            form.add_error('id_prod', 'El código escaneado es inválido.')
            return self.form_invalid(form)

        try:
            pedido = Pedido.objects.get(id=pedidoId)  # Buscamos el pedido
        except Pedido.DoesNotExist:
            form.add_error('id_prod', 'Producto no encontrado.')
            return self.form_invalid(form)

        # Si el pedido es válido, lo mostramos en el contexto
        self.pedido = pedido
        self.request.session['pedido_id'] = pedido.id
        print(pedido.cliente_nombre)
        print(pedido.id)
        # Si el pedido está en estado entregado, mostramos un mensaje
        if pedido.entregado:
            messages.error(self.request, "Este pedido ya ha sido entregado.")
            return self.form_invalid(form)

        # Ya no necesitamos redirigir, solo se actualiza el contexto
        return self.render_to_response(self.get_context_data())  # Volver a cargar la vista con el pedido cargado

    def form_invalid(self, form):
        print('formulario invalid')
        # Cuando el formulario es inválido, volvemos a cargar la vista con el formulario
        return self.get(self.request)
    
    

        
class TerminarDeEntregarPedidoView(VentasPermisoMixin,FormView):
    form_class = VentaVoucherForm
    success_url = '.'

    def form_valid(self, form):
        # Obtener el tipo de pago
        type_payment_saldo = form.cleaned_data['type_payment']

        # Recuperar el id del pedido de la sesión
        pedido_id = self.request.session.get('pedido_id')

        if not pedido_id:
            messages.error(self.request, "No se ha proporcionado un pedido válido.")
            return HttpResponseRedirect(reverse('pedidos_app:pedido-lista'))

        # Obtener el objeto Pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # Modificamos el pedido
        pedido.type_payment_saldo = type_payment_saldo
        pedido.date_entrega = timezone.now()
        pedido.entregado = True
        pedido.save()
        
        # Recopilamos los detalles del pedido
        mensaje = (
            f"🎉 *¡Pedido Entregado!* {pedido.amount} Bs 🎉\n\n"
            f"🛍️ *Detalles del Pedido:*\n\n"
            f"    📅 *Fecha de Inicio:* {pedido.date_sale}\n"
            f"    🧾 *Cliente:* {pedido.cliente_nombre}\n"
            f"    📱 *Celular:* {pedido.cliente_celular}\n"
            f"    🕒 *Fecha de Entrega:* {pedido.date_entrega}\n"
            f"    💳 *Tipo de Pago:* {pedido.type_payment_saldo}\n"
            f"    💰 *Saldo:* {pedido.saldo} BS\n"
            f"    💸 *Descuento Aplicado:* {pedido.descuento} BS\n"
            f"    💵 *Adelanto:* {pedido.adelanto} BS\n"

            
            f"🔍 *Descripción:* {pedido.description}\n\n"
        )
        send_telegram_message(mensaje)
        # Limpiamos el pedido de la sesión después de actualizar
        self.request.session.pop('pedido_id', None)

        # Mensaje de éxito
        messages.success(self.request, f"Pedido {pedido.id} entregado exitosamente.")
        
        # Redirigimos de nuevo a la vista de entrega para mostrar el siguiente pedido
        return HttpResponseRedirect(reverse('pedidos_app:pedido-entregar'))

    def form_invalid(self, form):
        # Si el formulario no es válido, volvemos a cargar la vista
        return self.render_to_response(self.get_context_data())

@csrf_exempt
def vaciar_carrito(request):
    if request.method == 'POST':
        # Encuentra el carrito asociado al usuario actual
        carrito = CartP.objects.filter(user=request.user, productos_cargados=True).first()
        if carrito:
            # Eliminar los productos asociados al carrito
            carrito.items.all().delete()  # Elimina las instancias de CarShopPed asociadas
            carrito.productos_cargados = False  # Cambia el estado a 'false'
            carrito.save()  # Guarda los cambios en el carrito
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'no_cart_found'})  # Si no hay carrito
    return JsonResponse({'status': 'invalid_method'}, status=400)

