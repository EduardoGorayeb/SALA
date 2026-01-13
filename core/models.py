from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth import get_user_model

class PendingSignup(models.Model):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=255)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

                                                                 
class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('email_verificado', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superusuário precisa ter is_superuser=True.')

        return self.create_user(email, nome, password, **extra_fields)


                                                          
class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100, verbose_name="Nome completo")
    email_verificado = models.BooleanField(default=False)
    token_verificacao = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(default=timezone.now)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email
    
User = get_user_model()

class Relatorio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tema = models.CharField(max_length=300)
    dados_json = models.JSONField()
    token_pdf = models.CharField(max_length=64, null=True, blank=True)
    tipo_discurso = models.CharField(
        max_length=50,
        choices=[
            ("tcc", "TCC / Defesa acadêmica"),
            ("palestra_tecnica", "Palestra técnica"),
            ("palestra_motivacional", "Palestra motivacional"),
            ("pitch_comercial", "Pitch comercial"),
            ("pitch_startup", "Pitch startup"),
            ("videoaula", "Videoaula"),
            ("explicacao_escolar", "Explicação escolar"),
            ("apresentacao_comercial_detalhada", "Apresentação comercial detalhada"),
            ("livre", "Livre")
        ],
        default="livre"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tema