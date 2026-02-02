from restaurant.models import Dish, OrderItem, Table, Order
from rest_framework import serializers


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price']


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'number', 'capacity', 'is_available', 'validation_code']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'dish', 'quantity', 'observations']
        read_only_fields = ['price', 'order']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_price', 'type', 'table', 'status', 'payment_confirmed', 'items']
        read_only_fields = ['total_price', 'created_at', 'payment_confirmed']

    def create(self, validated_data):
        # Remove os itens do payload para criar o pedido primeiro
        items_data = validated_data.pop('items')
        
        # Cria o Pedido (Order)
        order = Order.objects.create(total_price=0, **validated_data)
        
        total_accumulated = 0

        # Loop para criar os itens e somar o total
        for item_data in items_data:
            dish = item_data['dish'] # Pega o objeto Prato
            quantity = item_data['quantity']
            
            # Pega o preço atual do prato do banco de dados (Segurança)
            current_price = dish.price
            
            # Cria o Item vinculado ao Pedido
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=quantity,
                price=current_price, # Grava o preço unitário histórico
                observations=item_data.get('observations', '')
            )
            
            # Soma ao total do pedido
            total_accumulated += (current_price * quantity)

        # Atualiza o preço total do pedido e salva
        order.total_price = total_accumulated # type: ignore
        order.save()

        return order