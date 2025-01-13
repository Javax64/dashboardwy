from django import forms

from applications.productos.models import Producto
from .models import Sale
class VentaForm(forms.Form):
    productId = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        required=False,
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control ps-5'})
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
    def clean_count(self):
        count = self.cleaned_data['count']
        if count < 1:
            raise forms.ValidationError('Ingrese una cantidad mayor a cero')

        return count


class VentaVoucherForm(forms.Form):

    type_payment = forms.ChoiceField(
        required=False,
        choices=Sale.TIPO_PAYMENT_CHOICES,
        widget=forms.Select(
            attrs = {
                'class': 'form-control',
            }
        )
    )
    type_invoce = forms.ChoiceField(
        required=False,
        choices=Sale.TIPO_INVOCE_CHOICES,
        widget=forms.Select(
            attrs = {
                'class': 'input-group-field',
            }
        )
    )
    descuento = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(
            attrs = {
                'value': '0',
                'class': 'form-control',
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
    