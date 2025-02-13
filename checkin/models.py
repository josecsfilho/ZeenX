from django.db import models

class Pedido(models.Model):
    numero_pedido = models.CharField(max_length=10, unique=True)
    nome_entregador = models.CharField(max_length=100)
    data_criacao = models.DateTimeField(auto_now_add=True)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.numero_pedido} - {self.nome_entregador} {'(Concluído)' if self.concluido else ''}"
