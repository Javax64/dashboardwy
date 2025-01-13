from django import forms

from applications.productos.models import Producto, Extra
from .models import Pedido
from datetime import datetime

class PedidoForm(forms.Form):
    productId = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        required=False,
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control ps-5', 'id': 'id_productId'})
    )
    count = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs = {
                'value': '1',
                'class': 'form-control ps-5',
            }
        )
    )
    
    
    extra = forms.ModelMultipleChoiceField(
        queryset=Extra.objects.all(),  # Asegúrate de que sea el queryset correcto
        required=False,  # Si es opcional, marca como False
        widget=forms.CheckboxSelectMultiple  # O un widget adecuado para selección múltiple
    )
    
    #
    def clean_count(self):
        count = self.cleaned_data['count']
        if count < 1:
            raise forms.ValidationError('Ingrese una cantidad mayor a cero')

        return count


class PedidoDatosForm(forms.Form):
    cliente_nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs = {
                'placeholder': 'Nombre Cliente',
                'class': 'form-control ps-5',
                
                'id':'cliente_nombre',
                
            }
        )
    )
    cliente_celular= forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs = {
                'placeholder': 'Celular Cliente',
                'class': 'form-control ps-5',
                
                'id':'cliente_celular',
                
            }
        )
    )
    entregado = forms.BooleanField(
        label='Pedido entregado',
        required=False,  # Si no es obligatorio, de lo contrario ponlo como True
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
                'type':'checkbox',
                'id':'flexSwitchCheckDefault',
                'name': 'entregado', 
                
            }
        )
    )

    type_payment = forms.ChoiceField(
        required=False,
        choices=Pedido.TIPO_PAYMENT_CHOICES,
        widget=forms.Select(
            attrs = {
                'class': 'form-select',
                'id':'id_type_payment',
            }
        )
    )
    
    # Campo para el descuento (debe ser un valor entero, mínimo 0)
    descuento = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(
            attrs={
                
                'class': 'form-control',
                'id': 'descuento',  # ID añadido para que sea accesible en el frontend
                'oninput': 'actualizarSaldo()',  # Event handler para actualizar el saldo cuando se cambie el descuento
                'placeholder':'0 Bs',
            }
        )
    )
    # Campo para el adelanto
    adelanto = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                'placeholder':'0 Bs',
                'class': 'form-control',
                'id': 'adelanto',  # ID para capturar el adelanto
                'oninput': 'actualizarSaldo()',  # Event handler para actualizar el saldo cuando se cambie el adelanto
            }
        )
    )

    # Campo para el saldo (se calcula automáticamente en el frontend, solo se muestra)
    saldo = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                'placeholder':'0 Bs',
                'class': 'form-control',
                'id': 'saldo',  # ID para capturar el saldo
                  # El saldo es solo de lectura, ya que se calcula
            }
        )
    )
    
    # Campo para la fecha de inicio (cuando comienza el pedido)
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control',
                'id': 'fecha_inicio',
                'placeholder': 'Fecha de Inicio...',
                'type':'date',
            }
        )
    )
    
    # Campo para la fecha de entrega
    fecha_entrega = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'result form-control',
                'id': 'date',  # Este ID es para la funcionalidad estética
                'data-id': 'fecha_entrega',  # Este ID adicional es para monitorizarlo
                'placeholder': 'Fecha de Entrega...',
                'type': 'date',
                'data-dtp': 'dtp_a0Sea',
            }
        )
    )
    
     # Campo para el tipo de entrega (en tienda, envío, o delivery)
    type_entrega = forms.ChoiceField(
        required=False,
        choices=[(0, 'En tienda'), (1, 'Envio'), (2, 'Delivery')],
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'id': 'tipo_entrega',
                'name':'tipo_entrega',
                'value': '0',
                
            }
        )
    )
    # Campo para el departamento (con la opción de "Otro..." y un campo para el nombre personalizado si es necesario)
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
        ('other', 'Otro...'),  # Esta es la opción que permitirá al usuario escribir otro departamento
    ]
    departamento = forms.ChoiceField(
        required=False,
        choices=DEPARTAMENTO_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'single-select',
                'id': 'departamento',
                'name':'departamento',
                 'onchange': 'toggleCustomInput()', # Llamar a la función JavaScript cuando se cambie la opción
            }
        )
    )
     # Campo para el nombre personalizado del departamento (si aplica)
    custom_department = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control mt-2',
                
                'name': 'custom-department',
                'placeholder': 'Escriba el nombre del departamento',
            }
        )
    )
    # Campo para la dirección de entrega
    direccion = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'direccion2',
                'placeholder': 'Dirección de entrega',
            }
        )
    )
    # Campo para la dirección de entrega
    direccionEnvio = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'direccion',
                'placeholder': 'Dirección de entrega',
            }
        )
    )
    # Campo para la dirección de entrega
    sucursal = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'sucursal',
                'placeholder': 'sucursal de entrega',
            }
        )
    )
    # Campo para la dirección de entrega
    carnet = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'carnet',
                'placeholder': 'Carnet del cliente',
            }
        )
    )
    # Campo para la dirección de entrega
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'description',
                'placeholder': 'Descrion del pedido',
            }
        )
    )
    

class ScanneQRForm(forms.Form):
    escaneado = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs = {
                'placeholder': 'escaneado',
                'class': 'input-group-field',
            }
        )
    )    
    id_prod = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs = {
                'placeholder': 'escaneado',
                'class': 'form-control ps-5',
                'id':'codigo_escaneado',
                'type': 'hidden',
            }
        )
    )
    #
class VentaVoucherForm(forms.Form):

    type_payment = forms.ChoiceField(
        required=False,
        choices=Pedido.TIPO_PAYMENT_CHOICES,
        widget=forms.Select(
            attrs = {
                'class': 'form-control',
            }
        )
    )
    