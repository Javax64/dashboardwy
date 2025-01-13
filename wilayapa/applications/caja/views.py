# django
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    View,
    TemplateView
)
#
from applications.venta.models import Sale, SaleDetail
from applications.users.mixins import VentasPermisoMixin
#
from .models import CloseBox
from .functions import detalle_ventas_no_cerradas


class ReporteCierreCajaView(VentasPermisoMixin, TemplateView):

    template_name = 'caja/cerrarCaja.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtramos las ventas para el usuario actual (self.request.user)
        context["ventas_dia"] = detalle_ventas_no_cerradas(user=self.request.user).order_by('-created')

        # Total vendido solo para el usuario actual
        context["total_vendido"] = Sale.objects.total_ventas_dia(user=self.request.user)

        # Total anulado solo para el usuario actual
        context["total_anulado"] = Sale.objects.total_ventas_anuladas_dia(user=self.request.user)

        # Totales por tipo de pago
        context["total_efectivo"] = Sale.objects.total_ventas_efectivo(user=self.request.user)
        context["total_transferencia"] = Sale.objects.total_ventas_transferencia(user=self.request.user)


        context["num_ventas_hoy"] = Sale.objects.ventas_no_cerradas().filter(user=self.request.user).count()

        return context


class ProcesoCerrarCajaView(VentasPermisoMixin,View):

    def post(self, request, *args, **kwargs):
        # cerramos las ventas
        num_cerradas, total = Sale.objects.cerrar_ventas(user=request.user)
        if num_cerradas > 0:
            CloseBox.objects.create(
                date_close=timezone.now(),
                count=num_cerradas,
                amount= total,
                user=self.request.user
            )
        
        return HttpResponseRedirect(
            reverse(
                'caja_app:caja-index'
            )
        )
    
