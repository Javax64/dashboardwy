from django import forms
from applications.users.models import User



class LiquidacionProviderForm(forms.Form):

    
    date_start = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'input-group-field',
            },
        )
    )
    date_end = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'input-group-field',
            },
        )
    )


class ResumenVentasForm(forms.Form):
    
    date_start = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
                'name' : 'fecha1',
                'id' : 'fecha1'
            },
        )
    )
    date_end = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
                'name' : 'fecha2',
                'id' : 'fecha2'
            },
        )
    )
    userId = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Usuarios",
        widget=forms.Select(attrs={'class': 'form-control ps-5', 'name': 'userId', 'id': 'userId'})
    )
    filtro_fecha = forms.ChoiceField(
        choices=[ ('entrega', 'Fecha de Entrega'),('inicio', 'Fecha de Inicio')],
        required=True,
        initial='entrega',
        widget=forms.RadioSelect
    )

