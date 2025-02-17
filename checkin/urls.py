from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('monitor/', views.monitor_view, name='monitor_view'),
    path('admin_pedidos/', views.admin_pedidos_view, name='admin_pedidos_view'),
    path('search_pedidos/', views.search_pedidos_view, name='search_pedidos'),
    path('excluir_pedido/<int:id>/', views.excluir_pedido, name='excluir_pedido'),
    path('atualizar_pedidos/', views.atualizar_pedidos, name='atualizar_pedidos'),
    path('marcar_concluido/<int:pedido_id>/', views.marcar_concluido, name='marcar_concluido'),
    path('', views.checkin_view, name='checkin_view'),
    path('listar-pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos_pendentes_json/', views.pedidos_pendentes_json, name='pedidos_pendentes_json')


]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)