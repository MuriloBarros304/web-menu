from django.db import models


class Order(models.Model):
    TYPE_CHOICES = [
        ('dine-in', 'Consumo no Local'),
        ('takeaway', 'Para Viagem'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendente/Aguardando Pagamento'),
        ('queued', 'Na Fila (Cozinha)'), # Status crucial para o FIFO da cozinha
        ('preparing', 'Em Preparação'),
        ('ready', 'Pronto'), # Garçom busca ou Cliente retira
        ('completed', 'Concluído'),
        ('canceled', 'Cancelado'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.PROTECT, verbose_name='Usuário', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço Total')
    type = models.CharField(max_length=50, verbose_name='Tipo de Pedido', choices=TYPE_CHOICES, default='dine-in')
    table = models.ForeignKey('Table', on_delete=models.PROTECT, verbose_name='Número da Mesa', blank=True, null=True)
    status = models.CharField(max_length=50, verbose_name='Status do Pedido', choices=STATUS_CHOICES,
    default='pending')
    payment_confirmed = models.BooleanField(default=False, verbose_name='Pagamento Confirmado')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido #{self.pk} - {self.get_status_display()}" # type: ignore

class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome do Prato')
    description = models.TextField(verbose_name='Descrição do Prato')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço do Prato')

    class Meta:
        verbose_name = 'Prato'
        verbose_name_plural = 'Pratos'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Pedido')
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, verbose_name='Prato')
    quantity = models.PositiveIntegerField(verbose_name='Quantidade')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço Unitário')
    observations = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True, verbose_name='Número da Mesa')
    capacity = models.PositiveIntegerField(blank=True, null=True, verbose_name='Capacidade da Mesa')
    is_available = models.BooleanField(default=True, verbose_name='Disponibilidade da Mesa')
    validation_code = models.CharField(max_length=10, unique=True, verbose_name='Código de Validação', blank=True, null=True)

    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
    
    def __str__(self):
        return f'Mesa {self.number}'