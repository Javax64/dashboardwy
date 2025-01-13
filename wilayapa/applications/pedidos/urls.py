from django.urls import path
from . import views

app_name = "pedidos_app"
urlpatterns = [
    path(
        'pedido/new-pedido/', 
        views.AddCarPedView.as_view(),
        name='pedido-nuevo',
    ),
    path(
        'pedido/update/<pk>/', 
        views.CarShopUpdateView.as_view(),
        name='pedido-update',
    ),
    path(
        'pedidos/delete/<pk>/', 
        views.CarShopDeleteView.as_view(),
        name='pedido-delete',
    ),
    path(
        'pedidos/delete-all/', 
        views.CarShopDeleteAll.as_view(),
        name='pedidos-delete_all',
    ),
    path(
        'pedido/datos/', 
        views.ProcesoPedidoGuardarView.as_view(),
        name='pedido-datos',
    ),
    path(
        'pedido/lista/', 
        views.PedidosListView.as_view(),
        name='pedido-lista',
    ),
    path(
        'pedido/anulate/<int:pk>/', 
        views.PedidoAnulateView.as_view(), 
        name='pedido-anulate'
    ),
    path('delete_image_ped/', 
         views.DeleteImageTicketView.as_view(), 
         name='delete_image_ped'
    ),
    path('eliminar_imagenes_ticket/', 
         views.EliminarImagenesTicketView.as_view(), 
         name='eliminar_imagenes_ticket'
    ),
    path('verificar_imagen_ticket/', 
         views.VerificarImagenTicketView.as_view(), 
         name='verificar_imagen_ticket'
    ),
    path(
        'pedido/ProcesoPedidoEditarView/<int:id>/', 
        views.ProcesoPedidoEditarView.as_view(), 
        name='pedido-editar'
    ),
    path(
        'pedido/editar_guardar/<int:id>/', 
        views.PedidoGuardarView.as_view(),
        name='pedido-editar-guardar',
    ),
    path(
        'pedido/detalle/<int:pk>/', 
        views.DetallePedidoView.as_view(), 
        name='pedido-detalle'
    ),
    
    path(
        'pedido/entregar/', 
        views.entregaPedidoView.as_view(), 
        name='pedido-entregar'
    ),
    path(
        'pedido/terminar/', 
        views.TerminarDeEntregarPedidoView.as_view(), 
        name='pedido-entregar-terminar'
    ),

    # URL para actualizar la cantidad de un producto en el carrito
    path('pedido/update_car_shop/<int:pk>/', views.EditCarShopUpdateView.as_view(), name='car-shop-update'),

    # URL para eliminar un producto del carrito
    path('pedido/delete_car_shop/<int:pk>/', views.EditCarShopDeleteView.as_view(), name='car-shop-delete'),

    # URL para eliminar todos los productos del carrito
    path('pedido/delete_all_car_shop/', views.EditCarShopDeleteAll.as_view(), name='car-shop-delete-all'),

    #cvaciar el carrito si se sale de la pagina
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    
]
