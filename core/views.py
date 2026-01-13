from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import re
import threading
import sys
from .pdf_service import gerar_pdf_weasy
import subprocess
import os
from pathlib import Path
import json
import uuid
from django.core.cache import cache
from django.utils.timezone import now
from .models import Usuario, PendingSignup, Relatorio
from django.utils.timezone import localtime
import asyncio
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

@login_required(login_url='login')
def relatorio(request):
    return render(request, 'core/relatorio_analise.html')

def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        errors = []
        if not nome or not email or not senha or not confirmar_senha:
            errors.append('Preencha todos os campos.')
        if nome and not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', nome):
            errors.append('O nome deve conter apenas letras e espaços.')
        if nome and len(nome.replace(" ", "")) < 3:
            errors.append('O nome deve ter pelo menos 3 letras.')
        if senha and confirmar_senha and senha != confirmar_senha:
            errors.append('As senhas não coincidem.')
        if email and Usuario.objects.filter(email=email).exists():
            errors.append('Este e-mail já está cadastrado.')
        if errors:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            for e in errors:
                messages.error(request, e)
            return render(request, 'usuarios/cadastro.html')
        token = get_random_string(64)
        expires_at = timezone.now() + timedelta(hours=24)
        PendingSignup.objects.filter(email=email).delete()
        PendingSignup.objects.create(
            email=email,
            nome=nome,
            password_hash=make_password(senha),
            token=token,
            expires_at=expires_at
        )
        verify_link = request.build_absolute_uri(reverse('verificar_email')) + f'?token={token}'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'verify_link': verify_link, 'nome': nome, 'email': email})
        context = {'cadastro_sucesso': True, 'nome': nome, 'email': email, 'verify_link': verify_link}
        return render(request, 'usuarios/cadastro.html', context)
    return render(request, 'usuarios/cadastro.html')

def verificar_email(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, 'Token inválido.')
        return redirect('login')
    try:
        pending = PendingSignup.objects.get(token=token)
    except PendingSignup.DoesNotExist:
        messages.error(request, 'Token inválido ou expirado.')
        return redirect('login')
    if pending.is_expired():
        pending.delete()
        messages.error(request, 'Token expirado. Faça o cadastro novamente.')
        return redirect('cadastro')
    if Usuario.objects.filter(email=pending.email).exists():
        pending.delete()
        messages.info(request, 'Este e-mail já está verificado. Faça login.')
        return redirect('login')
    usuario = Usuario(email=pending.email, nome=pending.nome, email_verificado=True, is_active=True)
    usuario.password = pending.password_hash
    usuario.save()
    pending.delete()
    messages.success(request, 'E-mail verificado com sucesso! Faça login.')
    return redirect('login')

def enviar_email_async(assunto, mensagem, destinatarios):
    def _enviar():
        send_mail(assunto, mensagem, settings.DEFAULT_FROM_EMAIL, destinatarios, fail_silently=True)
    threading.Thread(target=_enviar).start()

def logar_usuario(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        if not email or not senha:
            messages.error(request, 'Preencha todos os campos.')
            return render(request, 'usuarios/login.html')
        usuario = authenticate(request, email=email, password=senha)
        if usuario is not None:
            if not usuario.email_verificado:
                messages.info(request, 'Confirme seu e-mail antes de fazer login.')
                return render(request, 'usuarios/login.html')
            login(request, usuario)
            nome_raw = (usuario.nome or '').strip()
            primeiro_nome = nome_raw.split()[0] if nome_raw else usuario.email.split('@')[0]
            messages.success(request, f'Bem-vindo(a), {primeiro_nome}!')
            return redirect('index')
        else:
            if Usuario.objects.filter(email=email).exists():
                messages.warning(request, 'A senha informada está incorreta.')
                return render(request, 'usuarios/login.html')
            pending = PendingSignup.objects.filter(email=email).first()
            if pending:
                if pending.is_expired():
                    pending.delete()
                    messages.info(request, 'Seu link expirou. Faça cadastro novamente.')
                    return render(request, 'usuarios/login.html')
                messages.info(request, 'Sua conta ainda não foi verificada.')
                return render(request, 'usuarios/login.html')
            messages.error(request, 'Usuário não encontrado.')
            return render(request, 'usuarios/login.html')
    return render(request, 'usuarios/login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')

def redefinir_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Informe seu e-mail.')
            return render(request, 'usuarios/redefinir_senha.html')
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, 'E-mail não encontrado.')
            return render(request, 'usuarios/redefinir_senha.html')
        token = get_random_string(64)
        usuario.token_verificacao = token
        usuario.save()
        reset_link = request.build_absolute_uri(reverse('confirmar_redefinicao')) + f'?token={token}'
        context = {'reset_sent': True, 'reset_link': reset_link, 'email': usuario.email}
        return render(request, 'usuarios/redefinir_senha.html', context)
    return render(request, 'usuarios/redefinir_senha.html')

def confirmar_redefinicao(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, 'Token inválido.')
        return redirect('login')
    try:
        usuario = Usuario.objects.get(token_verificacao=token)
    except Usuario.DoesNotExist:
        messages.error(request, 'Token inválido ou expirado.')
        return redirect('login')
    if request.method == 'POST':
        n = request.POST.get('senha')
        c = request.POST.get('confirmar_senha')
        if not n or not c:
            messages.error(request, 'Preencha todos os campos.')
            return render(request, 'usuarios/redefinir_senha_confirmar.html')
        if n != c:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'usuarios/redefinir_senha_confirmar.html')
        usuario.set_password(n)
        usuario.token_verificacao = None
        if not usuario.email_verificado:
            usuario.email_verificado = True
        usuario.save()
        messages.success(request, 'Senha redefinida.')
        return redirect('login')
    return render(request, 'usuarios/redefinir_senha_confirmar.html')

@login_required(login_url='login')
def treino(request):
    return render(request, 'core/treino.html')

@login_required(login_url='login')
def historico(request):
    relatorios = Relatorio.objects.filter(usuario=request.user).order_by('-criado_em')
    lista = []
    for r in relatorios:
        lista.append({
            "id": r.id,
            "tema": r.tema,
            "criado_em": localtime(r.criado_em).strftime("%d/%m/%Y"),
            "dados": r.dados_json
        })
    return render(request, 'core/historico.html', {"relatorios_json": lista})

@login_required(login_url='login')
def gravar(request):
    return render(request, 'core/gravar.html')

@login_required(login_url='login')
def enviar_video(request):
    return render(request, 'core/enviar-video.html')

def atualizar_status_sala(process_id, progresso, mensagem, status="processing", redirect=None):
    cache.set(
        f"sala_status_{process_id}",
        {
            "progresso": progresso,
            "mensagem": mensagem,
            "status": status,
            "redirect": redirect,
            "atualizado_em": now().isoformat()
        },
        timeout=3600
    )

def processar_sala_worker(process_id, usuario_id, tema, tipo_discurso, contexto_apresentacao, caminho_video_str):
    try:
        ia_base = Path(settings.BASE_DIR) / "IA"
        ia_data = ia_base / "data"
        reports_dir = ia_data / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        progresso_atual = 1
        atualizar_status_sala(process_id, progresso_atual, "Preparando análise")

        process = subprocess.Popen(
            [
                sys.executable,
                str((ia_base / "run_sala.py").resolve()),
                caminho_video_str,
                tema,
                tipo_discurso,
                contexto_apresentacao
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(ia_base)
        )

        for linha in process.stdout:
            linha = linha.strip()
            if not linha:
                continue
            if not linha.startswith("[SALA]"):
                continue
            progresso = None
            mensagem = linha.replace("[SALA]", "").strip()
                                                           
            if "Inicializando analisador" in linha:
                progresso = 2
            elif "Preparando diretórios" in linha:
                progresso = 3
            elif "Extraindo áudio" in linha:
                progresso = 5
            elif "Áudio extraído" in linha:
                progresso = 10
            elif "Iniciando transcrição" in linha:
                progresso = 15
            elif "Carregando pipeline" in linha:
                progresso = 20
            elif "Pipeline de diarização carregado" in linha:
                progresso = 30
            elif "Iniciando análise de tom" in linha:
                progresso = 40
            elif "Análise de voz concluída" in linha:
                progresso = 50
            elif "Apresentador identificado" in linha:
                progresso = 55
            elif "Limpando áudio" in linha:
                progresso = 60
            elif "Áudio limpo salvo" in linha:
                progresso = 65
            elif "Gemini) do áudio limpo" in linha:
                progresso = 70
            elif "Gemini) OK" in linha:
                progresso = 75
            elif "Transcrição salva" in linha:
                progresso = 80
            elif "Analisando linguagem" in linha:
                progresso = 85
            elif "Calculando métricas" in linha:
                progresso = 90
            elif "Gerando feedback" in linha:
                progresso = 95
            elif "Relatório salvo" in linha:
                progresso = 98
            elif "sucesso" in linha:
                progresso = 100
            if progresso is not None:
                if progresso > progresso_atual:
                    progresso_atual = progresso
                atualizar_status_sala(process_id, progresso_atual, mensagem)

        process.wait()

        json_nome = f"SALA_{Path(caminho_video_str).stem}_report.json"
        caminho_json = Path(settings.BASE_DIR) / "IA" / "data" / "reports" / json_nome

        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)

        usuario = Usuario.objects.get(pk=usuario_id)

        rel = Relatorio.objects.create(
            usuario=usuario,
            tema=tema,
            tipo_discurso=tipo_discurso,
            dados_json=dados
        )

        atualizar_status_sala(
            process_id,
            100,
            "Redirecionando",
            status="completed",
            redirect=f"/sala/relatorio/{rel.id}/"
        )

        Path(caminho_video_str).unlink(missing_ok=True)

    except Exception as e:
        atualizar_status_sala(process_id, 100, f"Erro: {str(e)}", status="error")

@login_required(login_url='login')
def iniciar_analise_sala(request):
    if request.method != "POST":
        return JsonResponse({"erro": "metodo_invalido"}, status=405)

    tema = request.POST.get("tema")
    tipo = request.POST.get("tipo_discurso")
    contexto = request.POST.get("contexto_apresentacao", "")
    video = request.FILES.get("video")

    if not tema or not video or not tipo:
        return JsonResponse({"erro": "dados_incompletos"}, status=400)

    ia_base = Path(settings.BASE_DIR) / "IA"
    inputs_dir = ia_base / "data" / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    caminho_video = inputs_dir / video.name
    with open(caminho_video, "wb") as f:
        for chunk in video.chunks():
            f.write(chunk)

    process_id = uuid.uuid4().hex
    atualizar_status_sala(process_id, 1, "Iniciando")

    thread = threading.Thread(
        target=processar_sala_worker,
        args=(process_id, request.user.id, tema, tipo, contexto, str(caminho_video)),
        daemon=True
    )
    thread.start()

    return JsonResponse({"process_id": process_id})

@login_required(login_url='login')
def status_analise_sala(request, process_id):
    dados = cache.get(f"sala_status_{process_id}")
    if not dados:
        return JsonResponse({"status": "not_found"}, status=404)
    return JsonResponse(dados)

@login_required(login_url='login')
def pagina_relatorio(request, id):
    relatorio = get_object_or_404(Relatorio, id=id, usuario=request.user)
    return render(request, "core/relatorio.html", {"relatorio": relatorio})

@login_required
def verificar_duplicado(request):
    tema = request.GET.get("tema")
    tipo = request.GET.get("tipo")

    existe = Relatorio.objects.filter(tema=tema, tipo_discurso=tipo, usuario=request.user).exists()

    return JsonResponse({"duplicado": existe})

def relatorio_pdf_html(request, relatorio_id):
    token = request.GET.get("token")
    relatorio = get_object_or_404(Relatorio, id=relatorio_id)

    if token != relatorio.token_pdf:
        return HttpResponse("Acesso restrito.", status=403)

    dados = relatorio.dados_json
    return render(request, "pdf/relatorio_pdf.html", {
        "dados": dados,
        "relatorio": relatorio
    })

@login_required(login_url='login')
def relatorio_pdf(request, relatorio_id):
    relatorio = get_object_or_404(Relatorio, id=relatorio_id, usuario=request.user)

    if not relatorio.token_pdf:
        relatorio.token_pdf = uuid.uuid4().hex
        relatorio.save()

    url = request.build_absolute_uri(
        reverse("relatorio_pdf_html", args=[relatorio_id])
    ) + f"?token={relatorio.token_pdf}"

    pdf_bytes = gerar_pdf_weasy(url)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="relatorio_{relatorio_id}.pdf"'
    return response
@login_required(login_url='login')
def excluir_relatorio(request, relatorio_id):
    relatorio = get_object_or_404(Relatorio, id=relatorio_id, usuario=request.user)
    if request.method == 'POST':
        relatorio.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required(login_url='login')
def excluir_relatorios(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Dados inválidos'}, status=400)

    if not ids:
        return JsonResponse({'error': 'Nenhum relatório selecionado'}, status=400)

    relatorios = Relatorio.objects.filter(id__in=ids, usuario=request.user)
    deleted_count = relatorios.count()
    relatorios.delete()

    return JsonResponse({'success': True, 'deleted_count': deleted_count})

@login_required(login_url='login')
def comparacao_relatorios(request):
    relatorios = Relatorio.objects.filter(usuario=request.user).order_by('criado_em')
    lista_relatorios = []
    for r in relatorios:
        lista_relatorios.append({
            "id": r.id,
            "tema": r.tema,
            "criado_em": localtime(r.criado_em).strftime("%d/%m/%Y %H:%M"),
            "tipo_discurso": r.get_tipo_discurso_display(),
            "final_score": r.dados_json.get('final_score', 0)
        })
    return render(request, 'core/comparacao.html', {"relatorios_json": lista_relatorios})

