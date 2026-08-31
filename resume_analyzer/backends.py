from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows logging in using either
    username or email address (case-insensitive).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Search for user matching username (case-insensitive) OR email (case-insensitive)
        user_queryset = User.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username)
        )

        for user in user_queryset:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return None
