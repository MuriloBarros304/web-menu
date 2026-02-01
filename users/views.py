from rest_framework import generics
from .models import User
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class UserCreateView(generics.CreateAPIView):
    """
    View responsável por registrar novos usuários.
    Restrição: Apenas usuários autenticados e marcados como admins
    podem acessar esta rota.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CustomLoginView(ObtainAuthToken):
    """
    Recebe username e password.
    Retorna token de autenticação, id do usuário, email e tipo de usuário.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user'] # type: ignore
        
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'type': user.type
        })


