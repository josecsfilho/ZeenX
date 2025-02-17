from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Pedido


# 🔹 CHECK-IN DOS ENTREGADORES 🔹 #
def checkin_view(request):
    if request.method == 'POST':
        numero_pedido = request.POST.get('numero_pedido', '').strip().upper()
        nome_entregador = request.POST.get('nome_entregador', '').strip().upper()

        # Verifica se ambos os campos estão preenchidos
        if not numero_pedido or not nome_entregador:
            messages.error(request, "Preencha todos os campos.")
        # Verifica se o pedido já foi registrado
        elif Pedido.objects.filter(numero_pedido=numero_pedido).exists():
            messages.error(request, "Este pedido já foi registrado.")
        else:
            # Cria o novo pedido
            Pedido.objects.create(numero_pedido=numero_pedido, nome_entregador=nome_entregador)
            messages.success(request, "Check-in realizado com sucesso!")

        # Redireciona novamente para a página de check-in
        return redirect('checkin_view')

    # Caso o método seja GET, apenas renderiza o formulário de check-in
    return render(request, 'checkin/checkin.html')

# 🔹 CHECK-IN DOS ENTREGADORES 🔹 #








# 🔹 LOGIN 🔹 #
@csrf_exempt
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

# 🔹 LOGIN 🔹 #


# 🔹 LOGOUT (SAIR)
@login_required
def logout_view(request):
    logout(request)
    return redirect("login_view")

#  ADMINISTRAÇÃO DE PEDIDOS
@login_required
def admin_pedidos_view(request):
    """Renderiza a página principal do admin de pedidos."""

    pedidos_pendentes = Pedido.objects.filter(concluido=False).order_by('-data_criacao')
    pedidos_concluidos = Pedido.objects.filter(concluido=True).order_by('-data_criacao')[:5]

    paginator = Paginator(pedidos_pendentes, 10)  # Paginação
    page = request.GET.get('page')
    pedidos_pendentes_page = paginator.get_page(page)

    context = {
        'pedidos_pendentes': pedidos_pendentes_page,  # Usando a página de pedidos
        'pedidos_concluidos': pedidos_concluidos,
    }

    return render(request, 'checkin/admin_pedidos.html', context)

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


# def admin_pedidos_view(request):
#     """Renderiza a página principal do admin de pedidos."""
#     return render(request, 'checkin/admin_pedidos.html')


def search_pedidos_view(request):
    """Retorna os pedidos filtrados com base no número do pedido."""
    query = request.GET.get('search', '')

    if query:
        pedidos = Pedido.objects.filter(
            numero_pedido__icontains=query)  # Alterar conforme o nome do campo no seu modelo
    else:
        pedidos = []

    return render(request, 'checkin/search_results.html', {'pedidos': pedidos})



## admin_pedidos

def pedidos_pendentes(request):
    pedidos_pendentes = Pedido.objects.filter(status='pendente').order_by('-data_criacao')
    pedidos_concluidos = Pedido.objects.filter(status='concluido').order_by('-data_criacao')[:5]
    return render(request, 'admin_pedidos.html', {
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_concluidos': pedidos_concluidos
    })


def pedidos_pendentes_json(request):
    pedidos_pendentes = Pedido.objects.filter(status='pendente').order_by('-data_criacao')
    pedidos_concluidos = Pedido.objects.filter(status='concluido').order_by('-data_criacao')[:5]

    pedidos_ativos = [{
        'id': pedido.id,
        'numero_pedido': pedido.numero_pedido,
        'nome_entregador': pedido.nome_entregador,
        'data_criacao': pedido.data_criacao,
    } for pedido in pedidos_pendentes]

    ultimos_concluidos = [{
        'id': pedido.id,
        'numero_pedido': pedido.numero_pedido,
        'nome_entregador': pedido.nome_entregador,
        'data_criacao': pedido.data_criacao,
    } for pedido in pedidos_concluidos]

    return JsonResponse({
        'pedidos_ativos': pedidos_ativos,
        'ultimos_concluidos': ultimos_concluidos
    })