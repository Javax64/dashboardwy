from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from applications.users.mixins import VentasPermisoMixin,AdminPermisoMixin
from django.views.generic.edit import (
    FormView
)
from django.views.generic import (
    View,
    UpdateView,
    DeleteView,
    DeleteView,
    TemplateView,
    DetailView,
    ListView
)
# Create your views here.
from .forms import VentaForm, VentaVoucherForm,ScanneQRForm
from .models import Sale, SaleDetail, CarShop, Cart
from applications.productos.models import Producto
from .functions import procesar_venta, send_telegram_message
class AddCarView(VentasPermisoMixin,FormView):
    template_name = 'venta/index.html'
    form_class = VentaForm
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Verifica si el carrito existe para el usuario actual, si no, crea uno
        cart, created = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        context["productos"] = CarShop.objects.filter(cart=cart).order_by('-created')
        context["total_cobrar"] = CarShop.objects.total_cobrar(self.request.user)
        # formulario para venta con voucher
        context['form_voucher'] = VentaVoucherForm
        context['form_scanned'] = ScanneQRForm
        return context
    
    def form_valid(self, form):
        print('validadndo form')
        prodcutoId = form.cleaned_data['productId']
        count = form.cleaned_data['count']
        scaneado = form.cleaned_data['id_prod']
        print(scaneado)
        cart, created = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        if prodcutoId:

            producto = Producto.objects.get(id=prodcutoId.id)
            
            # Verificar si hay suficiente stock
            if producto.count < count:
                form.add_error('count', 'No hay suficiente stock para agregar esta cantidad al carrito.')
                return self.form_invalid(form)


            obj, created = CarShop.objects.get_or_create(
                barcode=prodcutoId.id,
                cart=cart,
                defaults={
                    'product': Producto.objects.get(id=prodcutoId.id),
                    'count': count
                }
            )
            #
            if not created:
                obj.count = obj.count + count
                obj.save()
        elif scaneado:
            try:
                productoId = int(scaneado.replace("Prd:", "").strip())  # Asignar el ID correcto
            except ValueError:
                # Si no se puede convertir el valor a entero, agregar un mensaje de error
                form.add_error('id_prod', 'El código escaneado es inválido.')
                return self.form_invalid(form)
            try:
                producto = Producto.objects.get(id=productoId)
            except Producto.DoesNotExist:
                form.add_error('productId', 'Producto no encontrado.')
                return self.form_invalid(form)
             # Crear o actualizar el producto en CarShop
            # Verificar si hay suficiente stock
            if producto.count < count:
                form.add_error('count', 'No hay suficiente stock para agregar esta cantidad al carrito.')
                return self.form_invalid(form)
            obj, created = CarShop.objects.get_or_create(
                barcode=productoId,  # Usamos el ID del producto
                cart = cart,
                defaults={
                    'product': producto,
                    'count': count
                }
            )

            if not created:
                obj.count += count  # Si ya existe, se aumenta la cantidad
                obj.save()

        return super(AddCarView, self).form_valid(form)
    
class CarShopUpdateView(VentasPermisoMixin,View):
    """ quita en 1 la cantidad en un carshop """

    def post(self, request, *args, **kwargs):
        car = CarShop.objects.get(id=self.kwargs['pk'])
        if car.count > 1:
            car.count = car.count - 1
            car.save()
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )

class CarShopDeleteView(VentasPermisoMixin,DeleteView):
    model = CarShop
    success_url = reverse_lazy('venta_app:venta-index')


class CarShopDeleteAll(VentasPermisoMixin,View):
    
    def post(self, request, *args, **kwargs):
        #
        cart = Cart.objects.get(user=request.user, is_active=True)
        print("entrandoa  elminar todos los datos")
        # Eliminamos solo los productos del carrito seleccionado
        CarShop.objects.filter(cart=cart).delete()
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )




class ProcesoVentaSimpleView(VentasPermisoMixin,View):
    """ Procesa una venta simple """

    def post(self, request, *args, **kwargs):
        #
        procesar_venta(
            self=self,
            type_invoce=Sale.SIN_COMPROBANTE,
            type_payment=Sale.CASH,
            user=self.request.user,
        )
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )
    
class ProcesoVentaVoucherView(VentasPermisoMixin,FormView):
    form_class = VentaVoucherForm
    success_url = '.'
    
    def form_valid(self, form):
        type_payment = form.cleaned_data['type_payment']
        type_invoce = form.cleaned_data['type_invoce']
        descuento = form.cleaned_data['descuento']
        print("descuento")
        print(descuento)
        #
        productos_sin_stock, venta = procesar_venta(
            self=self,
            descuento =descuento,
            type_invoce=type_invoce,
            type_payment=type_payment,
            user=self.request.user,
        )
        #
        productos2 = ", ".join(productos_sin_stock)
        # Verificar si no hay productos en el carrito
        if venta is None:
            messages.error(self.request, f"No hay productos en el carrito para realizar la venta o subiste un producto sin stock. {productos2}")
            return HttpResponseRedirect(reverse('venta_app:venta-index'))

        if productos_sin_stock:
            # Si hay productos sin stock, agregamos un mensaje de error
            productos2 = ", ".join(productos_sin_stock)
            messages.error(self.request, f"No hay suficiente stock para los siguientes productos: {productos2}.")
            return HttpResponseRedirect(reverse('venta_app:venta-index'))
        
        

        return HttpResponseRedirect(reverse('venta_app:venta-index'))
        
class SaleListView(VentasPermisoMixin,ListView):
    template_name = 'venta/ventas.html'
    context_object_name = "ventas" 

    def get_queryset(self):
        return Sale.objects.ventas_no_cerradas().filter(user=self.request.user).order_by('-date_sale')

class SaleDeleteView(VentasPermisoMixin,DetailView):
    template_name = "venta/delete.html"
    model = Sale
    print('entrnado al view')
    

    
    
class SaleAnulateView(VentasPermisoMixin,View):
    """ Anula la venta, pero no la elimina de la BD. Devuelve los productos al stock y
    descuenta del numero de venta de los productos """
    
    def post(self, request, *args, **kwargs):
        sale = Sale.objects.get(id = self.kwargs['pk'])
        print("ID de la venta: ", self.kwargs['pk'])
        # No se elimina realmente de la base de datos, solo se coloca como anulado. Por temas de                  auditoria
        sale.anulate = True
        sale.save()
        # actualizamos el stok y ventas
        SaleDetail.objects.restablecer_stok_num_ventas(sale.id)
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )
    
class VistaUsuarioView(VentasPermisoMixin,TemplateView):
    template_name = "venta/menu.html"