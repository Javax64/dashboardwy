from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    ListView
)
from django.db.models import Count
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from applications.venta.models import Sale, SaleDetail
from applications.pedidos.models import Pedido, PedidoDetail 
from applications.productos.models import Producto
from applications.users.models import User
from applications.users.mixins import AdminPermisoMixin
#
from .forms import LiquidacionProviderForm, ResumenVentasForm
#
from .functions import detalle_resumen_ventas,detalle_resumen_ventas2,detalle_ventas_no_cerradas,detalle_pedidos_no_anulados
from django.db.models import Q, Sum, F, FloatField, ExpressionWrapper,Case, When, Value
from django.utils import timezone
import json
class PanelHomeView(AdminPermisoMixin,TemplateView):
    template_name = "home/index.html"

class PanelAdminView(AdminPermisoMixin,TemplateView):
    template_name = "administracion/adminVentas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_ventas"] = Sale.objects.total_ventas_dia()
        context["total_anulaciones"] = Sale.objects.total_ventas_anuladas_dia()
        context["stok_cero"] = Producto.objects.productos_en_cero().count()

        # Resumen de ventas por fecha
        resumen_semana = SaleDetail.objects.resumen_ventas()[:7]
        context["resumen_semana"] = resumen_semana

         # Resumen de ventas por fecha y usuario
        resumen_por_usuario = {}

        for venta in resumen_semana:
            fecha = venta['sale__date_sale__date']  # Obtenemos la fecha de la venta
            
            # Filtramos las ventas por fecha
            ventas_por_usuario = SaleDetail.objects.filter(
                sale__date_sale__date=fecha,
                sale__anulate=False,
                sale__close=True
            ).values('sale__user').annotate(
                total_vendido=Sum(
                    F('price_sale') * F('count'),
                    output_field=FloatField()
                ),
                total_ganancias=Sum(
                    F('price_sale') * F('count'),
                    output_field=FloatField()
                ),
                num_ventas=Sum('count'),
                total_efectivo=Sum(
                    Case(
                        When(sale__type_payment='1', then=F('price_sale') * F('count')),
                        default=Value(0),
                        output_field=FloatField()
                    )
                ),
                total_transferencia=Sum(
                    Case(
                        When(sale__type_payment='0', then=F('price_sale') * F('count')),
                        default=Value(0),
                        output_field=FloatField()
                    )
                ),
            )

            # Guardamos en el diccionario, agrupando por fecha
            resumen_por_usuario[fecha] = ventas_por_usuario

        # Incluimos el resumen por usuario en el contexto
        context["resumen_por_usuario"] = resumen_por_usuario
        return context

class ReporteAdmin(AdminPermisoMixin, ListView):
    template_name = "home/reporte_admin.html"
    context_object_name = "resumen_ventas_mes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_ventas"] = Sale.objects.total_ventas()
        return context
    
    def get_queryset(self):
        return SaleDetail.objects.resumen_ventas_mes()
    


class ReporteLiquidacion(AdminPermisoMixin, ListView):
    template_name = "home/reporte_liquidacion.html"
    context_object_name = "ventas_liquidacion"
    extra_context = {'form': LiquidacionProviderForm}
    
    def get_queryset(self):
        
        lista_ventas, total_ventas = SaleDetail.objects.resumen_ventas_proveedor(
            provider=self.request.GET.get("provider", ''),
            date_start=self.request.GET.get("date_start", ''),
            date_end=self.request.GET.get("date_end", ''),
        )
        self.extra_context.update({'total_ventas': total_ventas})
        return lista_ventas


class ReporteResumenVentas(AdminPermisoMixin,ListView):
    template_name = "administracion/resumen_ventas.html"
    context_object_name = "resumen_ventas"
    extra_context = {'form': ResumenVentasForm}
    paginate_by = 40
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenemos los parámetros del filtro
        fecha_1 = self.request.GET.get("date_start", '')
        fecha_2 = self.request.GET.get("date_end", '')
        estado = self.request.GET.get("estado", '')
        pago = self.request.GET.get("pago", '')
        user_id = self.request.GET.get("userId", '')

        # Validamos las fechas
        fecha1, fecha2 = self.validar_fechas(fecha_1, fecha_2)

        # Obtenemos la lista de ventas filtrada
        lista_ventas = self.get_queryset()
        
        # Calculamos el total vendido y el total de ventas hoy aplicando los mismos filtros
        context["total_vendido"] = lista_ventas.aggregate(Sum('amount'))['amount__sum']  # Usamos 'amount' en lugar de 'total'
        context["total_vendido_dia"] = lista_ventas.filter(date_sale__date=timezone.now().date()).aggregate(Sum('amount'))['amount__sum']
        context["num_ventas_hoy"] = lista_ventas.count()

        # Totales por tipo de pago
        context["total_efectivo"] = lista_ventas.filter(type_payment=Sale.EFECTVO).aggregate(Sum('amount'))['amount__sum']
        context["total_transferencia"] = lista_ventas.filter(type_payment=Sale.TRANSFERENCIA).aggregate(Sum('amount'))['amount__sum']
        
        context["usuarios_reg"] = User.objects.all()

        return context
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
            fecha_1 = fecha_actual - timedelta(days=365)
            fecha_2 = fecha_actual + timedelta(days=365)
        
        # Asegurarse de que las fechas son válidas y coherentes
        if fecha_1 > fecha_2:
           fecha_2 = fecha_actual + timedelta(days=365)
        
        # Devolvemos las fechas procesadas
        return fecha_1, fecha_2
    def get_queryset(self):
        fecha_1 = self.request.GET.get("date_start", '')
        fecha_2 = self.request.GET.get("date_end", '')
        estado = self.request.GET.get("estado", '')
        pago = self.request.GET.get("pago", '')
        fecha1, fecha2 = self.validar_fechas(fecha_1,fecha_2)
        user_id = self.request.GET.get("userId", '')
        
        print(pago)

        lista_ventas = detalle_resumen_ventas(
            fecha1,
            fecha2,
            
        )
        # Verificación del tipo de pago
        if pago in ['0', '1']:  # Si el tipo de pago es 0 o 1, lo filtramos
            pago_filtro = int(pago)
        else:
            pago_filtro = None  # Si el pago no es 0 ni 1, no filtramos por tipo de pago
        if user_id:
            try:
                user_filtro = User.objects.get(id=user_id)
                lista_ventas = lista_ventas.filter(user=user_filtro)  # Asumiendo que cada venta tiene un campo 'user'
            except User.DoesNotExist:
                lista_ventas = lista_ventas.none()  # Si no se encuentra el usuario, no se retornan resultados
        
        # Filtramos según el estado y el tipo de pago
        if estado == 'Cerradas':
            if pago_filtro is not None:
                return lista_ventas.filter(close=True, anulate=False, type_payment=pago_filtro)
            else:
                return lista_ventas.filter(close=True, anulate=False)
        
        elif estado == 'Anuladas':
            print("filtrando ventas anuladas")
            lista_ventas2 = detalle_resumen_ventas2(fecha1, fecha2)
            if pago_filtro is not None:
                return lista_ventas2.filter(anulate=True, type_payment=pago_filtro)
            else:
                return lista_ventas2.filter(anulate=True)
        
        elif estado == 'NoCerradas':
            if pago_filtro is not None:
                return lista_ventas.filter(close=False, type_payment=pago_filtro)
            else:
                return lista_ventas.filter(close=False)
        
        else:  # Si no se especifica un estado, solo filtramos por el tipo de pago si es necesario
            if pago_filtro is not None:
                return lista_ventas.filter(type_payment=pago_filtro)
            else:
                return lista_ventas  
            
class ReporteResumenPedidos(AdminPermisoMixin,ListView):
    template_name = "administracion/admin_pedidos.html"
    context_object_name = "resumen_pedidos"
    extra_context = {'form': ResumenVentasForm}
    paginate_by = 40
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenemos los parámetros del filtro
        fecha_1 = self.request.GET.get("date_start", '')
        fecha_2 = self.request.GET.get("date_end", '')
        estado = self.request.GET.get("estado", '')
        pago = self.request.GET.get("pago", '')
        user_id = self.request.GET.get("userId", '')
        filtro_fecha = self.request.GET.get("filtro_fecha", 'inicio')
        print(filtro_fecha)
        # Validamos las fechas
        fecha1, fecha2 = self.validar_fechas(fecha_1, fecha_2)
        
        # Obtenemos la lista de pedidos filtrada
        lista_pedidos = detalle_pedidos_no_anulados().order_by('-date_entrega')

        

        # Agregar el listado de ventas al contexto
         # Filtramos según las fechas
        if fecha1 and fecha2:
            if filtro_fecha == 'inicio':  # Si es fecha de inicio
                print("entrando al filtro de inicio")
                print(fecha1)
                print(fecha2)
                
                lista_pedidos = lista_pedidos.filter(date_sale__range=[fecha1, fecha2])  # Filtramos por date_start
                print(lista_pedidos)
            else:  # Si es fecha de entrega
                lista_pedidos = lista_pedidos.filter(date_entrega__range=[fecha1, fecha2])  # Filtramos por date_entrega
        context['ventas'] = lista_pedidos
        
        # Filtramos según el estado del pedido
        if estado == 'Entregados':
            pedidos_filtrados = lista_pedidos.filter(anulate=False,entregado=True)
        elif estado == 'Anulados':
            pedidos_filtrados = lista_pedidos.filter(anulate=True)
        elif estado == 'Pendientes':
            pedidos_filtrados = lista_pedidos.filter(anulate=False,entregado=False)
        else:
            pedidos_filtrados = lista_pedidos.filter(anulate=False)

        # Filtramos por el usuario
        if user_id:
            try:
                user_filtro = User.objects.get(id=user_id)
                pedidos_filtrados = pedidos_filtrados.filter(user=user_filtro)
            except User.DoesNotExist:
                pedidos_filtrados = pedidos_filtrados.none()

        # Filtramos por tipo de pago
        if pago in ['0', '1']:  # Si el tipo de pago es 0 o 1, lo filtramos
            pago_filtro = int(pago)
            pedidos_filtrados = pedidos_filtrados.filter(type_payment_saldo=pago_filtro)

        # Ordenamos los pedidos por la fecha en orden descendente
        pedidos_filtrados = pedidos_filtrados.order_by('-date_entrega')

        # Calculamos el total vendido y el total de ventas hoy aplicando los mismos filtros
        total_vendido1 = pedidos_filtrados.filter(anulate=False).aggregate(Sum('adelanto'))['adelanto__sum'] or 0
        total_vendido2 = pedidos_filtrados.filter(anulate=False, entregado=True).aggregate(Sum('saldo'))['saldo__sum'] or 0
        
        context["total_vendido"] = total_vendido1 + total_vendido2  # Total de monto vendido
        context["total_vendido_dia"] = pedidos_filtrados.filter(date_sale__date=timezone.now().date()).aggregate(Sum('amount'))['amount__sum']

        # Calculamos el número de ventas hoy con los filtros aplicados
        context["num_ventas_hoy"] = pedidos_filtrados.count()

        # Totales por tipo de pago (adelanto y saldo)
        context["total_efectivo"] = pedidos_filtrados.filter(type_payment=Pedido.EFECTVO,anulate=False).aggregate(Sum('adelanto'))['adelanto__sum']
        
        context["total_transferencia"] = pedidos_filtrados.filter(type_payment=Pedido.TRANSFERENCIA,anulate=False).aggregate(Sum('adelanto'))['adelanto__sum']
        
        context["total_efectivo_saldo"] = pedidos_filtrados.filter(type_payment_saldo=Pedido.EFECTVO_S,anulate=False,entregado=True).aggregate(Sum('saldo'))['saldo__sum']
        
        context["total_transferencia_saldo"] = pedidos_filtrados.filter(type_payment_saldo=Pedido.TRANSFERENCIA_S,anulate=False,entregado=True).aggregate(Sum('saldo'))['saldo__sum']
        busqueda =  lista_pedidos.filter(type_payment="", entregado = False)
        print(busqueda)

        # Finalmente, pasamos los pedidos filtrados al contexto
        context["pedidos_filtrados"] = pedidos_filtrados
        context["usuarios_reg"] = User.objects.all()

        return context
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
            fecha_1 = fecha_actual - timedelta(days=365)
            fecha_2 = fecha_actual + timedelta(days=365)
        
        # Asegurarse de que las fechas son válidas y coherentes
        if fecha_1 > fecha_2:
           fecha_2 = fecha_actual + timedelta(days=365)
        
        # Devolvemos las fechas procesadas
        return fecha_1, fecha_2
    def get_queryset(self):
        fecha_1 = self.request.GET.get("date_start", '')
        fecha_2 = self.request.GET.get("date_end", '')
        estado = self.request.GET.get("estado", '')
        pago = self.request.GET.get("pago", '')
        fecha1, fecha2 = self.validar_fechas(fecha_1, fecha_2)
        user_id = self.request.GET.get("userId", '')

        lista_pedidos = Pedido.objects.all()

        # Filtramos según las fechas
        if fecha1 and fecha2:
            lista_pedidos = lista_pedidos.filter(date_entrega__range=[fecha1, fecha2])

        # Filtramos según el tipo de pago
        if pago in ['0', '1']:  # Si el tipo de pago es 0 o 1, lo filtramos
            pago_filtro = int(pago)
            lista_pedidos = lista_pedidos.filter(type_payment_saldo=pago_filtro)

        # Filtramos según el estado (entregado, anulado)
        if estado == 'Entregados':
            lista_pedidos = lista_pedidos.filter(entregado=True)
        elif estado == 'Anulados':
            lista_pedidos = lista_pedidos.filter(anulate=True)

        # Filtramos por usuario si es necesario
        if user_id:
            try:
                user_filtro = User.objects.get(id=user_id)
                lista_pedidos = lista_pedidos.filter(user=user_filtro)
            except User.DoesNotExist:
                lista_pedidos = lista_pedidos.none()

        return lista_pedidos  
            

class DashboardView(AdminPermisoMixin,TemplateView):
    template_name = "administracion/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todas las ventas (puedes aplicar filtros si lo necesitas)
        ventas = Sale.objects.all()

        # Agrupar las ventas por mes usando el campo 'date_sale' y contar las ventas por mes
        ventas_por_mes = ventas.filter(anulate=False).annotate(
            month=TruncMonth('date_sale')
        ).values('month').annotate(
            total_ventas=Sum('amount'),
            cantidad_ventas=Count('id')  # Contamos el número de ventas por mes
        ).order_by('month')

        # Obtener las sumas de ventas por mes (monto total)
        revenue_data = [int(venta['total_ventas'] or 0) for venta in ventas_por_mes]

        # Obtener la cantidad de ventas por mes
        cantidad_ventas_data = [int(venta['cantidad_ventas'] or 0) for venta in ventas_por_mes]
        # Calcular el porcentaje de cambio en las ventas (por cantidad de ventas)
        porcentaje_cambio_ventas = 0
        if len(cantidad_ventas_data) > 1:  # Comprobamos que haya más de un mes de datos
            ventas_mes_anterior = cantidad_ventas_data[-2]
            ventas_mes_actual = cantidad_ventas_data[-1]

            if ventas_mes_anterior != 0:  # Evitar división por cero
                porcentaje_cambio_ventas = ((ventas_mes_actual - ventas_mes_anterior) / ventas_mes_anterior) * 100
        context['porcentaje_cambio'] = round(porcentaje_cambio_ventas, 2)
        # Calcular el porcentaje de cambio en las ganancias (por monto total)
        porcentaje_cambio_ganancia = 0
        if len(revenue_data) > 1:  # Comprobamos que haya más de un mes de datos
            ganancia_mes_anterior = revenue_data[-2]
            ganancia_mes_actual = revenue_data[-1]

            if ganancia_mes_anterior != 0:  # Evitar división por cero
                porcentaje_cambio_ganancia = ((ganancia_mes_actual - ganancia_mes_anterior) / ganancia_mes_anterior) * 100
        
        # Redondear el porcentaje de cambio en las ganancias
        context['porcentaje_cambio_ganancia'] = round(porcentaje_cambio_ganancia, 2)

        # Si no hay ventas para algunos meses, rellenarlos con 0
        all_months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        months_map = dict(zip(range(1, 13), all_months))  # Mapeo de números de mes a nombres de mes

        # Asegúrate de que los datos tengan un valor para cada mes, incluso si no hay ventas en ese mes
        final_data = []
        cantidad_final_data = []

        for month in range(1, 13):
            # Datos de ventas por monto
            month_data = next((venta['total_ventas'] for venta in ventas_por_mes if venta['month'].month == month), 0)
            # Datos de cantidad de ventas
            cantidad_data = next((venta['cantidad_ventas'] for venta in ventas_por_mes if venta['month'].month == month), 0)

            # Convierte el valor a float antes de agregarlo a la lista
            final_data.append(float(month_data) if month_data else 0)
            cantidad_final_data.append(int(cantidad_data) if cantidad_data else 0)

        context['revenue_data'] = final_data  # Ventas por monto por mes
        context['cantidad_ventas_data'] = cantidad_final_data  # Cantidad de ventas por mes

        # Calcular el total de ventas (sumar el campo 'amount', ajusta el nombre según tu modelo)
        total_ventas = ventas.filter(anulate=False).aggregate(Sum('amount'))['amount__sum'] or 0  # Si no hay ventas, devuelve 0

        # Calcular las ventas del día actual
        total_ventas_dia = ventas.filter(anulate=False).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Obtener todos los pedidos (si usas el modelo Pedido)
        pedidos = Pedido.objects.all()
        # Agrupar los pedidos por mes, asegurándonos de sumar solo el saldo de los entregados
        pedidos_por_mes = pedidos.filter(anulate=False).annotate(
            month=TruncMonth('date_sale')
        ).values('month').annotate(
            total_ganancias=Sum(
                Case(
                    When(entregado=True, then=F('adelanto') + F('saldo')),  # Para pedidos entregados sumamos adelanto y saldo
                    default=F('adelanto'),  # Para pedidos no entregados solo sumamos el adelanto
                )
            ),
            cantidad_pedidos=Count('id')  # Contamos el número de pedidos por mes
        ).order_by('month')
        
        # Obtener la cantidad de pedidos por mes
        ganancias_pedidos_data = [float(pedido['total_ganancias'] or 0) for pedido in pedidos_por_mes]
        cantidad_pedidos_data = [int(pedido['cantidad_pedidos'] or 0) for pedido in pedidos_por_mes]
        print("Ganancias de pedidos por mes")
        print(ganancias_pedidos_data)
        # Calcular el porcentaje de cambio en la cantidad de pedidos
        porcentaje_cambio_pedidos = 0
        if len(cantidad_pedidos_data) > 1:  # Si hay más de un mes de datos
            pedidos_mes_anterior = cantidad_pedidos_data[-2]
            pedidos_mes_actual = cantidad_pedidos_data[-1]

            if pedidos_mes_anterior != 0:  # Evitar división por cero
                porcentaje_cambio_pedidos = ((pedidos_mes_actual - pedidos_mes_anterior) / pedidos_mes_anterior) * 100

        # Redondear el porcentaje de cambio en la cantidad de pedidos
        context['porcentaje_cambio_pedidos'] = round(porcentaje_cambio_pedidos, 2)
        # Calcular el porcentaje de cambio en las ganancias de pedidos

        porcentaje_cambio_ganancia_pedidos = 0
        if len(ganancias_pedidos_data) > 1:  # Si hay más de un mes de datos
            ganancia_pedidos_mes_anterior = ganancias_pedidos_data[-2]
            ganancia_pedidos_mes_actual = ganancias_pedidos_data[-1]

            if ganancia_pedidos_mes_anterior != 0:  # Evitar división por cero
                porcentaje_cambio_ganancia_pedidos = ((ganancia_pedidos_mes_actual - ganancia_pedidos_mes_anterior) / ganancia_pedidos_mes_anterior) * 100

        # Redondear el porcentaje de cambio en las ganancias de pedidos
        context['porcentaje_cambio_ganancia_pedidos'] = round(porcentaje_cambio_ganancia_pedidos, 2)

        # Si no hay ventas para algunos meses, rellenarlos con 0
        all_months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        months_map = dict(zip(range(1, 13), all_months))  # Mapeo de números de mes a nombres de mes

        # Asegúrate de que los datos tengan un valor para cada mes, incluso si no hay ventas o pedidos en ese mes
        final_ventas_data = []
        cantidad_ventas_final_data = []
        cantidad_pedidos_final_data = []
        ganancias_pedidos_final_data = []
        for month in range(1, 13):
            # Datos de ventas por monto
            month_venta_data = next((venta['total_ventas'] for venta in ventas_por_mes if venta['month'].month == month), 0)
            # Datos de cantidad de ventas
            cantidad_venta_data = next((venta['cantidad_ventas'] for venta in ventas_por_mes if venta['month'].month == month), 0)
            # Datos de cantidad de pedidos
            cantidad_pedido_data = next((pedido['cantidad_pedidos'] for pedido in pedidos_por_mes if pedido['month'].month == month), 0)
            # Datos de ganancias por pedidos (adelanto + saldo)
            ganancias_pedido_data = next((pedido['total_ganancias'] for pedido in pedidos_por_mes if pedido['month'].month == month), 0)

            # Convierte el valor a float antes de agregarlo a la lista
            final_ventas_data.append(float(month_venta_data) if month_venta_data else 0)
            cantidad_ventas_final_data.append(int(cantidad_venta_data) if cantidad_venta_data else 0)
            cantidad_pedidos_final_data.append(int(cantidad_pedido_data) if cantidad_pedido_data else 0)
            ganancias_pedidos_final_data.append(float(ganancias_pedido_data) if ganancias_pedido_data else 0)

        context['revenue_data'] = final_ventas_data  # Ventas por monto por mes
        context['cantidad_ventas_data'] = cantidad_ventas_final_data  # Cantidad de ventas por mes
        context['cantidad_pedidos_data'] = cantidad_pedidos_final_data  # Cantidad de pedidos por mes
        context['ganancias_pedidos_data'] = ganancias_pedidos_final_data  # Ganancias por mes (adelanto + saldo)

        # Calcular el total de ventas
        total_ventas = ventas.filter(anulate=False).aggregate(Sum('amount'))['amount__sum'] or 0  # Si no hay ventas, devuelve 0

        # Calcular las ventas del día actual
        total_ventas_dia = ventas.filter(anulate=False).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calcular el total de pedidos
        total_pedidos = pedidos.filter(anulate=False).aggregate(
            total_adelanto=Sum('adelanto'),
            total_saldo=Sum('saldo')
        )

        # Sumamos ambos campos
        total_pedidos_dia = (total_pedidos['total_adelanto'] or 0) + (total_pedidos['total_saldo'] or 0)
        # Calcular las ganancias del día actual
        total_pedidos_dia1 = pedidos.filter(anulate=False).aggregate(Sum('adelanto'))['adelanto__sum'] or 0
        total_pedidos_dia2 = pedidos.filter(anulate=False, entregado=True).aggregate(Sum('saldo'))['saldo__sum'] or 0
        total_pedidos_dia = total_pedidos_dia1 + total_pedidos_dia2

        # Contar el número de pedidos y ventas
        numero_pedidos = pedidos.count()
        numero_ventas = ventas.count()  # Número de ventas



        ######################PRODUCTOS MAS VENDIDOS##############################
        # Obtener todas las ventas y detalles de pedidos (sin anulados)
        pedidos_detalles = PedidoDetail.objects.filter(anulate=False)
        ventas_detalles = SaleDetail.objects.filter(anulate=False)

        # Obtener productos y porcentajes (según la lógica que ya tenías)
        productos_pedidos = pedidos_detalles.values('product__codigo').annotate(
            total_vendido=Sum('count')
        ).order_by('-total_vendido')

        productos_ventas = ventas_detalles.values('product__codigo').annotate(
            total_vendido=Sum('count')
        ).order_by('-total_vendido')

        # Combinar los productos vendidos de ambos modelos
        productos = {}
        for producto in productos_pedidos:
            productos[producto['product__codigo']] = producto['total_vendido']
        
        for producto in productos_ventas:
            if producto['product__codigo'] in productos:
                productos[producto['product__codigo']] += producto['total_vendido']
            else:
                productos[producto['product__codigo']] = producto['total_vendido']

        # Ordenar por la cantidad vendida
        productos_ordenados = sorted(productos.items(), key=lambda x: x[1], reverse=True)

        # Preparar los datos para pasar al template
        productos_nombres = [item[0] for item in productos_ordenados]
        cantidades = [item[1] for item in productos_ordenados]

        # Calcular el total de productos vendidos
        total_vendidos = sum(cantidades)

        # Calcular los porcentajes de cada producto
        porcentajes = [(cantidad / total_vendidos) * 100 for cantidad in cantidades]

        # Crear una lista de tuplas (producto, porcentaje)
        productos_y_porcentajes = [(producto, porcentaje) for producto, porcentaje in zip(productos_nombres, porcentajes)]
        
        # Pasar los productos y porcentajes al template
        context['productos_y_porcentajes'] = json.dumps(productos_y_porcentajes)
        print(context['productos_y_porcentajes']) 
        # Agregar las variables al contexto
        context['total_ventas'] = total_ventas
        context['total_ventas_dia'] = total_ventas_dia
        context['total_pedidos_dia'] = total_pedidos_dia
        context['ventas'] = ventas  # Si también quieres pasar todas las ventas al template
        context['pedidos'] = pedidos  # Pasamos todos los pedidos al template
        context['numero_pedidos'] = numero_pedidos  # Número de pedidos
        context['numero_ventas'] = numero_ventas  # Número de ventas

        return context