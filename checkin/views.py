from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Pedido

# 🔹 LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("admin_pedidos_view")
        else:
            messages.error(request, "Usuário ou senha inválidos")
    return render(request, "checkin/admin_login.html")

# 🔹 LOGOUT (SAIR)
@login_required
def logout_view(request):
    logout(request)
    return redirect("login_view")

# 🔹 ADMINISTRAÇÃO DE PEDIDOS
@login_required
def admin_pedidos_view(request):
    pedidos_pendentes = Pedido.objects.filter(concluido=False).order_by('data_criacao')
    pedidos_concluidos = Pedido.objects.filter(concluido=True).order_by('-data_criacao')[:5]

    paginator = Paginator(pedidos_pendentes, 10)
    page = request.GET.get('page')
    pedidos_pendentes_page = paginator.get_page(page)

    return render(request, 'checkin/admin_pedidos.html', {
        'pedidos_pendentes': pedidos_pendentes_page,
        'pedidos_concluidos': pedidos_concluidos,
    })

# 🔹 MARCAR PEDIDO COMO CONCLUÍDO
@login_required
@require_POST
def marcar_concluido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.concluido = True
    pedido.save()
    return JsonResponse({'status': 'success', 'pedido_id': pedido_id})

# 🔹 EXCLUIR PEDIDO
@login_required
@require_POST
def excluir_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    pedido.delete()
    return JsonResponse({'status': 'success'})

# 🔹 CHECK-IN DOS ENTREGADORES
def checkin_view(request):
    if request.method == 'POST':
        numero_pedido = request.POST.get('numero_pedido', '').strip().upper()
        nome_entregador = request.POST.get('nome_entregador', '').strip().upper()

        if not numero_pedido or not nome_entregador:
            messages.error(request, "Preencha todos os campos.")
        elif Pedido.objects.filter(numero_pedido=numero_pedido).exists():
            messages.error(request, "Este pedido já foi registrado.")
        else:
            Pedido.objects.create(numero_pedido=numero_pedido, nome_entregador=nome_entregador)
            messages.success(request, "Check-in realizado com sucesso!")

        return redirect('checkin_view')

    return render(request, 'checkin/checkin.html')

# 🔹 MONITOR DE PEDIDOS
def monitor_view(request):
    pedidos_ativos = Pedido.objects.filter(concluido=False).order_by('data_criacao')[:20]
    ultimos_concluidos = Pedido.objects.filter(concluido=True).order_by('-data_criacao')[:3]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'pedidos_ativos': list(pedidos_ativos.values('id', 'numero_pedido', 'nome_entregador', 'data_criacao')),
            'ultimos_concluidos': list(ultimos_concluidos.values('id', 'numero_pedido', 'nome_entregador', 'data_criacao'))
        })

    return render(request, 'checkin/monitor.html', {
        'pedidos_ativos': pedidos_ativos,
        'ultimos_concluidos': ultimos_concluidos,
    })

# 🔹 ATUALIZAR PEDIDOS (AJAX)
def atualizar_pedidos(request):
    pedidos_pendentes = Pedido.objects.filter(concluido=False).order_by("data_criacao")[:25]
    pedidos_concluidos = Pedido.objects.filter(concluido=True).order_by("-data_criacao")[:5]

    paginator = Paginator(pedidos_pendentes, 6)
    page = request.GET.get("page", 1)
    pedidos_page = paginator.get_page(page)

    return JsonResponse({
        "pedidos_pendentes": list(pedidos_page.object_list.values("id", "numero_pedido", "nome_entregador")),
        "pedidos_concluidos": list(pedidos_concluidos.values("id", "numero_pedido", "nome_entregador")),
        "total_paginas": paginator.num_pages,
    })

# 🔹 LISTAGEM DE PEDIDOS
def listar_pedidos(request):
    pedidos_ativos = Pedido.objects.filter(concluido=False).values('numero_pedido', 'nome_entregador', 'data_criacao')
    ultimos_concluidos = Pedido.objects.filter(concluido=True).order_by('-data_criacao')[:5].values('numero_pedido', 'nome_entregador', 'data_criacao')

    return JsonResponse({
        'pedidos_ativos': list(pedidos_ativos),
        'ultimos_concluidos': list(ultimos_concluidos)
    })

def pedidos_pendentes_json(request):
    pedidos = Pedido.objects.filter(concluido=False).values('id', 'numero_pedido', 'nome_entregador')
    return JsonResponse(list(pedidos), safe=False)