from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from restaurant.models import Dish, Table, Order, OrderItem
from restaurant.serializers import DishSerializer, TableSerializer, OrderSerializer, OrderItemSerializer


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    
    def get_permissions(self):
        """
        Qualquer um pode VER o cardápio (GET).
        Apenas Admins podem CRIAR/EDITAR (POST, PUT, DELETE).
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAdminUser]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    # Permissão base aberta, pois anônimos podem criar pedidos na mesa.
    # Filtramos a segurança dentro do get_queryset e perform_create.
    permission_classes = [AllowAny]

    def get_queryset(self): # type: ignore
        """
        Filtragem de pedidos conforme o usuário e contexto:
        1. Cozinha (FIFO): Retorna fila de preparação.
        2. Staff: Vê tudo.
        3. Cliente Logado: Vê seus pedidos.
        4. Anônimo: Não vê nada (segurança).
        """
        user = self.request.user
        queryset = Order.objects.all()

        # Cenário 1: Tela da Cozinha
        # URL: /api/orders/?mode=kitchen
        if self.request.query_params.get('mode') == 'kitchen': # type: ignore
            if not user.is_staff:
                raise PermissionDenied("Apenas funcionários acessam a visão da cozinha.")
            
            # FIFO: Ordena por data (mais antigo primeiro) e filtra status relevantes
            return queryset.filter(
                status__in=['queued', 'preparing']
            ).order_by('created_at')

        # Cenário 2: Funcionários (Garçons/Gerentes) veem tudo
        if user.is_staff:
            return queryset

        # Cenário 3: Cliente Logado vê histórico próprio

        if user.is_authenticated:
            return queryset.filter(user=user)

        # Cenário 4: Anônimo (Segurança)
        # Se não está logado, não pode listar pedidos para evitar vazamento de dados.
        return queryset.none()

    def perform_create(self, serializer):
        """
        Regras de negócio ao criar um pedido (Order):
        1. Pedido para Viagem (Takeaway) EXIGE Login.
        2. Pedido na Mesa (Dine-in) EXIGE Validação de QR Code.
        3. Define status inicial conforme tipo de pedido.
        """
        user = self.request.user if self.request.user.is_authenticated else None
        data = self.request.data # type: ignore
        order_type = data.get('type', 'dine-in')

        # REGRA 1: Pedido para Viagem (Takeaway) EXIGE Login
        if order_type == 'takeaway':
            if not user:
                raise ValidationError({"detail": "Para pedidos de retirada, é necessário fazer login."})
            
            # Status inicial de retirada é pendente pagamento
            serializer.save(user=user, status='pending')

        # REGRA 2: Pedido na Mesa (Dine-in) EXIGE Validação de QR Code
        elif order_type == 'dine-in':
            table_id = data.get('table')
            validation_code = data.get('validation_code') # Frontend deve enviar isso

            if not table_id:
                raise ValidationError({"detail": "O número da mesa é obrigatório para consumo no local."})

            # Busca a mesa e valida o código
            table = get_object_or_404(Table, pk=table_id)
            
            # Se a mesa tiver um código definido, o cliente TEM que acertar
            if table.validation_code and table.validation_code != validation_code:
                raise ValidationError({"detail": "Código de validação da mesa incorreto. Escaneie o QR Code novamente."})

            # Se passou na validação:
            # Pedido nasce como 'queued' (vai direto pra cozinha) pois pagam na saída
            serializer.save(user=user, status='queued')

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def mark_ready(self, request, pk=None):
        """
        Ação rápida para a Cozinha marcar pedido como 'Pronto'
        URL: /api/orders/{id}/mark_ready/
        """
        order = self.get_object()
        order.status = 'ready'
        order.save()
        return Response({'status': 'Pedido marcado como pronto'})
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def mark_completed(self, request, pk=None):
        """
        Ação para o Garçom marcar que entregou ou finalizou
        URL: /api/orders/{id}/mark_completed/
        """
        order = self.get_object()
        order.status = 'completed'
        order.save()
        return Response({'status': 'Pedido finalizado'})
