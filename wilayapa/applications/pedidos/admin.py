from django.contrib import admin

# Register your models here.
from .models import Pedido,PedidoDetail,CarShopPed,CartP
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date_sale',
        'cliente_nombre',
        'cliente_nombre',
        'amount',
        'saldo',
        'entregado',
        'anulate',
    )
    list_filter = (  'entregado', )
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(PedidoDetail)
admin.site.register(CarShopPed)
admin.site.register(CartP)