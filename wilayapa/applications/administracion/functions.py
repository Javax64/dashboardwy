#
from django.db.models import Prefetch, F, FloatField, ExpressionWrapper
#
from applications.venta.models import Sale, SaleDetail
from applications.pedidos.models import Pedido, PedidoDetail


def detalle_resumen_ventas(date_start, date_end):
    # funcion que recupera ventas no anuladas en rango de fechas
    # Y, el detalle de venta de cada venta
    
    if date_start and date_end:
        ventas = Sale.objects.ventas_en_fechas(date_start, date_end)
        consulta = ventas.prefetch_related(
            Prefetch(
                'detail_sale', 
                queryset=SaleDetail.objects.filter(sale__id__in=ventas).annotate(
                    subtotal=ExpressionWrapper(
                        F('price_sale')*F('count'),
                        output_field=FloatField()
                    )
                )
            )
        )

        return consulta
    else:
        return []
def detalle_resumen_ventas2(date_start, date_end):
    # funcion que recupera ventas no anuladas en rango de fechas
    # Y, el detalle de venta de cada venta
    
    if date_start and date_end:
        ventas = Sale.objects.ventas_en_fechas_total(date_start, date_end)
        consulta = ventas.prefetch_related(
            Prefetch(
                'detail_sale', 
                queryset=SaleDetail.objects.filter(sale__id__in=ventas).annotate(
                    subtotal=ExpressionWrapper(
                        F('price_sale')*F('count'),
                        output_field=FloatField()
                    )
                )
            )
        )

        return consulta
    else:
        return []
    
def detalle_ventas_no_cerradas(user):
    # recuepramos arry de id de ventas no cerradas
    ventas = Sale.objects.filter(user=user, close=False, anulate=False)
    consulta = ventas.prefetch_related(
        Prefetch(
            'detail_sale', 
            queryset=SaleDetail.objects.filter(sale__id__in=ventas).annotate(
                subtotal=ExpressionWrapper(
                    F('price_sale')*F('count'),
                    output_field=FloatField()
                )
            )
        )
    )

    return consulta

def detalle_pedidos_no_anulados():
    # Recuperamos el queryset de ventas no anuladas
    pedidos = Pedido.objects.filter(anulate=False)
    
    # Prefetch de los detalles de la venta con el subtotal calculado
    consulta = pedidos.prefetch_related(
        Prefetch(
            'detail_sale', 
            queryset=PedidoDetail.objects.filter(pedido__id__in=pedidos)
            .annotate(
                subtotal=ExpressionWrapper(
                    F('price_sale') * F('count'),  # Calculamos el subtotal como precio * cantidad
                    output_field=FloatField()
                )
            )
        )
    )

    return consulta