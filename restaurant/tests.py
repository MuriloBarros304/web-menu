from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from restaurant.models import Table, Dish, Order

class RestaurantTests(APITestCase):
    
    def setUp(self):
        """
        Este método roda ANTES de cada teste.
        Usamos para preparar o terreno (criar usuários, mesas, pratos).
        """
        # 1. Cria um Usuário Comum
        self.user = User.objects.create_user(username='cliente', password='123', email='cliente@example.com', type='customer')
        
        # 2. Cria um Admin (para criar pratos)
        self.admin = User.objects.create_superuser(username='admin', password='123', email='admin@example.com', type='admin')
        
        # 3. Cria uma Mesa com código secreto
        self.table = Table.objects.create(number=1, validation_code='SEGREDO')
        
        # 4. Cria um Prato Ativo
        self.dish = Dish.objects.create(name='Hamburguer', price=25.00, description='Bom')
        
        # URLs (usamos reverse para não escrever '/api/orders/' na mão)
        self.url_orders = reverse('order-list') # Nome definido no router (basename='order')
        self.url_dishes = reverse('dish-list')

    def test_create_dish_permission(self):
        """
        Testa se apenas Admin pode criar pratos.
        """
        data = {'name': 'Pizza', 'price': '50.00', 'description': 'Massa fina'}
        
        # Tentativa 1: Cliente comum tentando criar (Deve falhar)
        self.client.force_authenticate(user=self.user) # type: ignore
        response = self.client.post(self.url_dishes, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Tentativa 2: Admin tentando criar (Deve passar)
        self.client.force_authenticate(user=self.admin) # type: ignore
        response = self.client.post(self.url_dishes, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dish.objects.count(), 2) # 1 do setup + 1 de agora

    def test_order_dine_in_success(self):
        """
        Testa um pedido na mesa com o código CORRETO.
        """
        self.client.force_authenticate(user=self.user) # type: ignore
        
        payload = {
            "type": "dine-in",
            "table": self.table.id, # type: ignore
            "validation_code": "SEGREDO", # Código correto
            "items": [
                {"dish": self.dish.id, "quantity": 2} # type: ignore
            ]
        }
        
        response = self.client.post(self.url_orders, payload, format='json')
        
        # Verificações
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'queued') # Deve nascer "Na Fila" # type: ignore
        self.assertEqual(float(response.data['total_price']), 50.00) # 2 * 25.00 # type: ignore

    def test_order_dine_in_wrong_code(self):
        """
        Testa a segurança: código errado deve bloquear o pedido.
        """
        self.client.force_authenticate(user=self.user) # type: ignore
        
        payload = {
            "type": "dine-in",
            "table": self.table.id, # type: ignore
            "validation_code": "CODIGO_ERRADO", # Erro intencional
            "items": [
                {"dish": self.dish.id, "quantity": 1} # type: ignore
            ]
        }
        
        response = self.client.post(self.url_orders, payload, format='json')
        
        # Esperamos erro 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # O pedido não deve ter sido criado no banco
        self.assertEqual(Order.objects.count(), 0)