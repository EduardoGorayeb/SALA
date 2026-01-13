from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    path('verificar-email/', views.verificar_email, name='verificar_email'),
    path('login/', views.logar_usuario, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redefinir-senha/', views.redefinir_senha, name='redefinir_senha'),
    path('confirmar-redefinicao/', views.confirmar_redefinicao, name='confirmar_redefinicao'),
    path('sala/treino/', views.treino, name='treino'),
    path('sala/historico/', views.historico, name='historico'),
    path('sala/gravar/', views.gravar, name='gravar'),
    path('sala/enviar-video/', views.enviar_video, name='enviar_video'),
    path('sala/analisar/iniciar/', views.iniciar_analise_sala, name='iniciar_analise_sala'),
    path('sala/analisar/status/<str:process_id>/', views.status_analise_sala, name='status_analise_sala'),
    path('sala/relatorio/<int:id>/', views.pagina_relatorio, name='pagina_relatorio'),
    path('sala/verificar-duplicado/', views.verificar_duplicado, name='verificar_duplicado'),
    path('relatorio/<int:relatorio_id>/pdf/', views.relatorio_pdf, name='relatorio_pdf'),
    path('relatorio/<int:relatorio_id>/pdf/html/', views.relatorio_pdf_html, name='relatorio_pdf_html'),
    path('excluir-relatorio/<int:relatorio_id>/', views.excluir_relatorio, name='excluir_relatorio'),
    path('excluir-relatorios/', views.excluir_relatorios, name='excluir_relatorios'),
    path('sala/comparacao/', views.comparacao_relatorios, name='comparacao_relatorios'),
]
