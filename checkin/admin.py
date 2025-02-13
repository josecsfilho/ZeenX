from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Pedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'nome_entregador', 'data_criacao', 'concluido', 'acao_concluir')
    list_filter = ('concluido',)
    search_fields = ('numero_pedido', 'nome_entregador')
    actions = ['marcar_como_concluido']

    def acao_concluir(self, obj):
        if not obj.concluido:
            return format_html('<a class="btn btn-sm btn-success" href="{}">Concluir</a>', f'/admin/checkin/pedido/{obj.id}/concluir/')
        return "✅ Concluído"
    acao_concluir.short_description = "Ação"
    acao_concluir.allow_tags = True

    def marcar_como_concluido(self, request, queryset):
        updated = queryset.update(concluido=True)
        self.message_user(request, f'{updated} pedido(s) marcado(s) como concluído(s).')
    marcar_como_concluido.short_description = "Marcar pedidos selecionados como concluídos"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:pedido_id>/concluir/', self.admin_site.admin_view(self.concluir_pedido), name='pedido-concluir'),
        ]
        return custom_urls + urls

    def concluir_pedido(self, request, pedido_id):
        Pedido.objects.filter(id=pedido_id).update(concluido=True)
        self.message_user(request, 'Pedido marcado como concluído.')
        return redirect(f'/admin/checkin/pedido/')




# from django.contrib import admin
# from .models import Pedido
#
# @admin.register(Pedido)
# class PedidoAdmin(admin.ModelAdmin):
#     list_display = ('numero_pedido', 'nome_entregador', 'data_criacao', 'concluido')
#     list_filter = ('concluido',)
#     search_fields = ('numero_pedido', 'nome_entregador')
#     actions = ['marcar_como_concluido']
#
#     def marcar_como_concluido(self, request, queryset):
#         queryset.update(concluido=True)
#     marcar_como_concluido.short_description = "Marcar pedidos selecionados como concluídos"
#
#
# # @admin.register(Pedido)
# # class PedidoAdmin(admin.ModelAdmin):
# #     list_display = ('numero_pedido', 'nome_entregador', 'data_criacao', 'status', 'concluir_pedido_link')
# #     list_filter = ('concluido',)
# #     search_fields = ('numero_pedido', 'nome_entregador')
# #     actions = ['marcar_como_concluido']
# #
# #     def status(self, obj):
# #         return "✅ Concluído" if obj.concluido else "⏳ Pendente"
# #     status.short_description = "Status"
# #
# #     def concluir_pedido_link(self, obj):
# #         if not obj.concluido:
# #             return f'<a href="/admin/checkin/pedido/{obj.id}/change/">Marcar como concluído</a>'
# #         return "✅"
# #     concluir_pedido_link.allow_tags = True
# #     concluir_pedido_link.short_description = "Ação"
# #
# #     def marcar_como_concluido(self, request, queryset):
# #         queryset.update(concluido=True)
# #     marcar_como_concluido.short_description = "Marcar pedidos selecionados como concluídos"