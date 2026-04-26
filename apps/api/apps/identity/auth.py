from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(username=username)
            if user.check_password(password) and user.is_active:
                return user
            return None
        except Usuario.DoesNotExist:
            return None
        except Exception:
            return None
        
    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None