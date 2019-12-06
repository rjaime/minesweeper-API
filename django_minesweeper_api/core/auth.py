from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

UserModel = get_user_model()

class SingleUserAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            user = UserModel.objects.all()[0]
        except:
            user = UserModel.objects.create_user(
                'common',
                email='common@minesweeperapichallenge.com',
                password='^c0mm0n!',
            )
        
        return (user, None)
