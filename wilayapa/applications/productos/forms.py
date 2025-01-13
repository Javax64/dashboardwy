from django import forms
from .models import Producto, Extra, Marca


class AddProductoForm(forms.Form):
    codigo = forms.CharField(
        label='Usuario',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control radius-0 ps-5',
                'placeholder': 'Codigo',
                
            }
        )
    )
    name = forms.CharField(
        label='Nombre Producto',
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nombre Producto',
                'class': 'form-control',
            }
        )
    )
    description = forms.CharField(
        label='Nombre Producto',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Descripcion del producto',
                'class': 'form-control',
            }
        )
    )
    
    marca = forms.ModelChoiceField(
        queryset=Marca.objects.all(),
        label='Marca Producto',
        required=False,
        widget=forms.Select(
            attrs={
                'placeholder': 'Genero ...',
                'class': 'form-select',
            }
        )
    )
    new_marc = forms.CharField(
        label='Nueva Marca',
        required=False,
        
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nueva Marca',
                'class': 'form-control',
                'display': 'none',
            }
        )
    )
    count = forms.IntegerField(
        label='Cantidad en Stock',
        required=True,
        min_value=0,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Cantidad',
                'class': 'form-control',
            }
        )
    )
    
    sale_price = forms.DecimalField(
        label='Precio de Venta',
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Precio de venta',
                'class': 'form-control',
            }
        )
    )
    extra = forms.ModelMultipleChoiceField(
        queryset=Extra.objects.all(),
        required=False,
        label="Extras",
        widget=forms.CheckboxSelectMultiple  # Permite seleccionar múltiples extras
    )
     # Campo para subir una imagen

    image = forms.ImageField(
        label='Imagen del Producto',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
                'id': 'formFile', 
                'type': 'file',
            }
        )
    )
    
     
    def clean(self):
        cleaned_data = super().clean()
        
        # Validación de la nueva marca
        if not cleaned_data.get('marca') and not cleaned_data.get('new_marc'):
            self.add_error('marca', 'Debes seleccionar una marca o registrar una nueva marca.')

        codigo = cleaned_data.get('codigo')
        if codigo and Producto.objects.filter(codigo=codigo).exists():
            self.add_error('codigo', 'El código ya está en uso. Por favor, elige uno diferente.')
        
        return cleaned_data
    


    
class NewExtraForm(forms.Form):

    nuevo_extra_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs = {
                'class': 'form-control',
                
            }
        )
    )
    nuevo_extra_price = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs = {
                'class': 'form-control',
                
            }
        )
    )
    def clean(self):
        cleaned_data = super().clean()

        # Validación: Si se ha ingresado un nombre pero no un precio, mostrar el error
        nuevo_extra_name = cleaned_data.get('nuevo_extra_name')
        nuevo_extra_price = cleaned_data.get('nuevo_extra_price')

        if nuevo_extra_name and not nuevo_extra_price:
            self.add_error('nuevo_extra_price', 'El precio del nuevo extra es obligatorio.')

        return cleaned_data
    


class uppdateProductoForm(forms.Form):
    codigo = forms.CharField(
        label='Usuario',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control radius-0 ps-5',
                'placeholder': 'Codigo',
                
            }
        )
    )
    name = forms.CharField(
        label='Nombre Producto',
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nombre Producto',
                'class': 'form-control',
            }
        )
    )
    description = forms.CharField(
        label='Nombre Producto',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Descripcion del producto',
                'class': 'form-control',
            }
        )
    )
    anulate = forms.BooleanField(
        label='Producto anulado',
        required=False,  # Si no es obligatorio, de lo contrario ponlo como True
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
            }
        )
    )
    
    marca = forms.ModelChoiceField(
        queryset=Marca.objects.all(),
        label='Marca Producto',
        required=False,
        widget=forms.Select(
            attrs={
                'placeholder': 'Genero ...',
                'class': 'form-select',
            }
        )
    )
    new_marc = forms.CharField(
        label='Nueva Marca',
        required=False,
        
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nueva Marca',
                'class': 'form-control',
                'display': 'none',
            }
        )
    )
    count = forms.IntegerField(
        label='Cantidad en Stock',
        required=True,
        min_value=0,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Cantidad',
                'class': 'form-control',
            }
        )
    )
    
    sale_price = forms.DecimalField(
        label='Precio de Venta',
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Precio de venta',
                'class': 'form-control',
            }
        )
    )
    extra = forms.ModelMultipleChoiceField(
        queryset=Extra.objects.all(),
        required=False,
        label="Extras",
        widget=forms.CheckboxSelectMultiple  # Permite seleccionar múltiples extras
    )
     # Campo para subir una imagen

    image = forms.ImageField(
        label='Imagen del Producto',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
                'id': 'formFile', 
                'type': 'file',
            }
        )
    )
    
     # Campo oculto para pasar el ID del producto
    producto_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    def clean(self):
        cleaned_data = super().clean()
        
        # Validación de la nueva marca
        if not cleaned_data.get('marca') and not cleaned_data.get('new_marc'):
            self.add_error('marca', 'Debes seleccionar una marca o registrar una nueva marca.')

        codigo = cleaned_data.get('codigo')

        if codigo:
            # Excluir el producto actual de la validación del código (usando el mismo código)
            if Producto.objects.filter(codigo=codigo).exclude(codigo=codigo).exists():
                self.add_error('codigo', 'El código ya está en uso. Por favor, elige uno diferente.')
        
        return cleaned_data
    
############################SCANNER PRODUCTOS #######################################
class ScannerForm(forms.Form):
    titulo = forms.CharField(
        required=False,
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Introduce el elemento a buscar',
                'class': 'form-control',
                'id': 'scanned_data',
            }
        )
    )
    productId = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    count = forms.IntegerField(
        label='Cantidad en Stock',
        required=False,
        min_value=0,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Cantidad',
                'class': 'form-control',
            }
        )
    )
    aumentar_stock = forms.BooleanField(
        label='Producto anulado',
        required=False,  # Si no es obligatorio, de lo contrario ponlo como True
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
            }
        )
    )
    solo_imprimir = forms.BooleanField(
        label='Producto anulado',
        required=False,  # Si no es obligatorio, de lo contrario ponlo como True
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
            }
        )
    )
    Productos_list = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label='Productos Registrados',
        required=False,
        widget=forms.Select(
            attrs={
                'placeholder': 'Productos ...',
                'class': 'form-select',
            }
        )
    )
    
class ScannerForm2(forms.Form):
    titulo2 = forms.CharField(
        required=True,
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Introduce el elemento a buscar',
                'class': 'form-control',
                'id': 'scanned_data',
            }
        )
    )