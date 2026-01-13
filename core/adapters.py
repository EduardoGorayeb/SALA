from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        user = sociallogin.user
        email = user.email

        if email:
            try:
                usuario_existente = Usuario.objects.get(email=email)
                sociallogin.connect(request, usuario_existente)
            except Usuario.DoesNotExist:
                pass

    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data

        nome_google = extra_data.get("name") or extra_data.get("given_name")
        if nome_google:
            user.nome = nome_google

        user.email_verificado = True
        user.is_active = True
        user.save()

        sociallogin.save(request)
        return user