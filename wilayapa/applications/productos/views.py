from django.shortcuts import render
from django.views.generic import FormView, ListView, DeleteView,UpdateView,View
# Create your views here.
#importando formularios
from .forms import AddProductoForm, NewExtraForm,uppdateProductoForm,ScannerForm,ScannerForm2
#importamos los modelos
from .models import Producto, Extra, Marca
from django.forms import formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect    
from applications.users.mixins import AlmacenPermisoMixin

class RegistrarProducto3(AlmacenPermisoMixin,FormView):
    template_name = "producto/add_product.html"
    form_class = AddProductoForm
    success_url = '.'  # Redirige a la página de éxito después del registro

    def get_context_data(self, **kwargs):
        # Llamamos a la implementación de la clase base para no perder su contexto
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los productos creados hasta ahora
        productos = Producto.objects.all()

        # Pasamos los productos al contexto
        context['productos'] = productos
        context['form_extras'] = formset_factory(NewExtraForm, extra=1)
        return context
    
    def form_valid(self, form):
        print("estamos en el form_valid")

        # Obtener los datos del formulario
        codigo = form.cleaned_data['codigo']
        name = form.cleaned_data['name']
        description = form.cleaned_data['description']
        marca = form.cleaned_data['marca']
        new_marc = form.cleaned_data['new_marc']
        count = form.cleaned_data['count']
        sale_price = form.cleaned_data['sale_price']
        extra_seleccionados = form.cleaned_data['extra']
        image = form.cleaned_data['image'] 

        # Si no se selecciona una marca y se proporciona una nueva marca, la creamos
        if not marca and new_marc:
            marca = Marca.objects.create(name=new_marc)

        # Crear el producto
        producto = Producto.objects.create(
            codigo=codigo,
            name=name,
            description=description,
            marca=marca,
            count=count,
            sale_price=sale_price,
            image=image 
        )
        # Asociar los extras seleccionados de la base de datos al producto
        for extra in extra_seleccionados:
            
            producto.extra.add(extra)

        

         # Procesar los nuevos extras enviados mediante el formset
        formset = formset_factory(NewExtraForm,extra=1)(self.request.POST)

        
       
        if formset.is_valid():
            for extra_form in formset:
                
                
                # Validar si tanto el nombre como el precio están presentes
                if extra_form.cleaned_data.get('nuevo_extra_name') and extra_form.cleaned_data.get('nuevo_extra_price'):
                    # Crear el nuevo extra
                    nuevo_extra = Extra.objects.create(
                        name=extra_form.cleaned_data['nuevo_extra_name'],
                        price=extra_form.cleaned_data['nuevo_extra_price']
                    )
                    # Asociar el nuevo extra al producto
                    producto.extra.add(nuevo_extra)
                else:
                    # Si falta el precio o el nombre, agregar el error
                    if not extra_form.cleaned_data.get('nuevo_extra_price'):
                        extra_form.add_error('nuevo_extra_price', 'El precio del nuevo extra es obligatorio.')
                    if not extra_form.cleaned_data.get('nuevo_extra_name'):
                        extra_form.add_error('nuevo_extra_name', 'El nombre del nuevo extra es obligatorio.')

        else:
            print("Errores en el formset:", formset.errors)
        return super(RegistrarProducto3, self).form_valid(form)

    
class ProductoListView(AlmacenPermisoMixin,ListView):
    template_name = "producto/lista.html"
    context_object_name = 'producto'
    def get_queryset(self):
        kword = self.request.GET.get("kword", '')
        order = self.request.GET.get("order", '')
        queryset = Producto.objects.buscar_producto(kword, order)
        return queryset

class ProductDeleteView(AlmacenPermisoMixin,DeleteView):
    template_name = "producto/delete.html"
    model = Producto
    success_url = reverse_lazy('producto_app:producto-lista')

class UpdateProductView(AlmacenPermisoMixin,FormView):
    template_name = "producto/update.html"
    form_class = uppdateProductoForm
    success_url = reverse_lazy('producto_app:producto-lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto_id = self.kwargs.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)
        form = self.form_class(initial={
            'codigo': producto.codigo,
            'name': producto.name,
            'description': producto.description,
            'marca': producto.marca,
            'count': producto.count,
            'sale_price': producto.sale_price,
            'extra': producto.extra.all(),
            'image': producto.image,
            'anulate': producto.anulate,

            'producto_id': producto.id,
        })
        context['form'] = form
        context['productos'] = producto
        context['form_extras'] = formset_factory(NewExtraForm, extra=1)
        print("**************************************************prudasdxasdasdsa")
        print(producto.extra.all())
        return context

    def form_valid(self, form):
        producto_id = self.kwargs.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)

        # Obtener datos del formulario
        codigo = form.cleaned_data['codigo']
        name = form.cleaned_data['name']
        description = form.cleaned_data['description']
        marca = form.cleaned_data['marca']
        new_marc = form.cleaned_data['new_marc']
        count = form.cleaned_data['count']
        anulate = form.cleaned_data['anulate']
        sale_price = form.cleaned_data['sale_price']
        extra_seleccionados = form.cleaned_data['extra']
        image = form.cleaned_data['image']

        # Si no se selecciona una marca y se proporciona una nueva marca, crearla
        if not marca and new_marc:
            marca = Marca.objects.create(name=new_marc)

        # Validación de código único
        if codigo != producto.codigo:
            producto_existente = Producto.objects.filter(codigo=codigo).first()
            if producto_existente:
                form.add_error('codigo', 'El código ya está en uso.')
                return self.form_invalid(form)

        # Actualizar el producto
        producto.codigo = codigo
        producto.name = name
        producto.description = description
        producto.marca = marca
        producto.count = count
        producto.anulate = anulate
        producto.sale_price = sale_price
        
        if image:
            producto.image = image
        producto.save()

        # Actualizar los extras
        producto.extra.set(extra_seleccionados)

        # Procesar formset de extras nuevos
        formset = formset_factory(NewExtraForm, extra=1)(self.request.POST)
        if formset.is_valid():
            for extra_form in formset:
                nuevo_extra_name = extra_form.cleaned_data.get('nuevo_extra_name')
                nuevo_extra_price = extra_form.cleaned_data.get('nuevo_extra_price')
                if nuevo_extra_name and nuevo_extra_price:
                    nuevo_extra = Extra.objects.create(name=nuevo_extra_name, price=nuevo_extra_price)
                    producto.extra.add(nuevo_extra)

        # Redirigir después de la actualización exitosa
        return super().form_valid(form)
    


class SacannerStockFormView(AlmacenPermisoMixin,FormView):
    template_name = "producto/scannerProd.html"
    form_class = ScannerForm
    success_url = reverse_lazy('producto_app:producto-scanner')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todos los productos
        context['productos'] = Producto.objects.all()
        context['form_scann'] = ScannerForm2
        context['productos2'] = list(Producto.objects.all().values('id', 'name'))
          # Pasamos los QR al contexto
        qr_image_path = os.path.join(settings.MEDIA_ROOT, 'qr_print/combined_qr_codes.png')
        context['combined_qr_image'] = '/media/qr_print/combined_qr_codes.png' if os.path.exists(qr_image_path) else None
        return context

    def form_valid(self, form):
        print(f"Datos POST: {self.request.POST}") 
        form_submit = self.request.POST.get('form_submit', None)
        
        print(f"Valor de form_submit: {form_submit}") 
        
        if form_submit == 'qrForm':
            print('entramos al form qrFomr')
            producto_id = form.cleaned_data['productId']  # Aquí es 'productId'
            cantidad_a_sumar = form.cleaned_data['count']  # 'count' es el campo para la cantidad
            if not cantidad_a_sumar or cantidad_a_sumar <= 0:
            # Si la cantidad es vacía o no válida, asignar 0 o un valor predeterminado
                cantidad_a_sumar = 0

            producto = get_object_or_404(Producto, id=producto_id.id)
            # Verificar si se debe aumentar el stock o solo generar e imprimir
            aumentar_stock = form.cleaned_data.get('aumentar_stock', False)  # Si está marcado
            solo_imprimir = form.cleaned_data.get('solo_imprimir', False)  # Si está marcado

            # Si "Aumentar stock" está seleccionado, actualizamos el stock
            if aumentar_stock:
                producto.count = producto.count + cantidad_a_sumar
                producto.save()
            # Generar los QR y almacenarlos en un campo en la base de datos o en el contexto
            qr = Producto.objects.generate_qr_codes(producto_id, cantidad_a_sumar)  # Guardamos los QR en un atributo de la vista
            print(qr)
            qr_print = Producto.objects.print_qr_codes(qr, cantidad_a_sumar)
            print(qr_print)
            return redirect(self.success_url)
        
        
        return super(SacannerStockFormView, self).form_valid(form)
    

class DeleteQRImageView(AlmacenPermisoMixin,View):
    success_url = reverse_lazy('producto_app:producto-scanner')
    def get(self, request, *args, **kwargs):
        # Ruta completa de la imagen
        qr_image_path = os.path.join(settings.MEDIA_ROOT, 'qr_print/combined_qr_codes.png')
        
        if os.path.exists(qr_image_path):
            os.remove(qr_image_path)
            return JsonResponse({'status': 'success', 'message': 'Imagen eliminada correctamente'})
        else:
            return JsonResponse({'status': 'error', 'message': 'La imagen no existe'})
        
class PruebaFormView(AlmacenPermisoMixin,FormView):
    form_class = ScannerForm2
    success_url = '.'
    def form_valid(self, form):
        print("***form valid de ScannerPrueba")
        prod_id = form.cleaned_data['titulo2']
        print('se recupero-------------------' + prod_id)
        """
        prod_id = prod_id.replace("Prd:", "")
        producto = get_object_or_404(Producto, id=prod_id)
        producto.count = producto.count + 1
        producto.save()
        """
        return HttpResponseRedirect(reverse('producto_app:producto-scanner'))

class ScannerInventario(AlmacenPermisoMixin,FormView):
    template_name = "producto/inventario.html"
    form_class = ScannerForm2
    success_url = reverse_lazy('producto_app:producto-inventario')
    def form_valid(self, form):
        print("***form valid de ScannerPrueba")
        prod_id = form.cleaned_data['titulo2']
        print('se recupero-------------------' + prod_id)
        """
        prod_id = prod_id.replace("Prd:", "")
        producto = get_object_or_404(Producto, id=prod_id)
        producto.count = producto.count + 1
        producto.save()
        """
        return super(ScannerInventario, self).form_valid(form)