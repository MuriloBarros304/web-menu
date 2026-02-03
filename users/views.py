from rest_framework import generics
from .models import User
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .serializers import UserProfileSerializer, UserSerializer, UserAdminSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

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
            'type': user.type,
        })
    

class UserViewSet(viewsets.ModelViewSet):
    """
    View para listar todos os usuários.
    Restrição: Apenas usuários autenticados e marcados como admins
    podem acessar esta rota.
    """
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def change_type(self, request, pk=None):
        """
        Ação customizada para alterar o tipo de um usuário.
        Apenas admins podem realizar esta ação.
        """
        me = self.request.user
        user = self.get_object()
        if str(me.pk) == str(user.pk):
            return Response({'error': 'Admins não podem alterar seu próprio tipo.'}, status=400)
        new_type = request.data.get('type')

        if new_type not in ['admin', 'staff', 'customer']:
            return Response({'error': 'Tipo inválido.'}, status=400)
        
        if new_type == user.type:
            return Response({'error': 'O usuário já é deste tipo.'}, status=400)

        user.type = new_type
        user.save()
        return Response({'status': 'Tipo de usuário atualizado.'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_active(self, request, pk=None):
        """
        Ação customizada para ativar/desativar um usuário.
        Apenas admins podem realizar esta ação.
        """
        me = self.request.user
        user = self.get_object()
        if str(me.pk) == str(user.pk):
            return Response({'error': 'Admins não podem desativar seu próprio usuário.'}, status=400)

        user.is_active = not user.is_active
        user.save()
        status_str = 'ativado' if user.is_active else 'desativado'
        return Response({'status': f'Usuário {status_str}.'})
    

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View para obter detalhes de um usuário específico.
    Restrição: Apenas usuários autenticados podem acessar esta rota.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self): # type: ignore
        return self.request.user


