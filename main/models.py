from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Категория")
    slug = models.SlugField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    title = models.CharField(max_length=100, verbose_name="Название товара")
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    release_date = models.DateField(auto_now=True, verbose_name="Дата добавления товара")
    link = models.CharField(max_length=1024, verbose_name="Ссылка на товар")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    @property
    def ct_model(self):
        return self._meta.model_name

class Customer(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    customer_orders = models.ManyToManyField("Order", blank=True, related_name="related_customer")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"


class Cart(models.Model):
    owner = models.ForeignKey(Customer, verbose_name="Покупатель", on_delete=models.CASCADE)
    products = models.ManyToManyField("CartProduct", blank=True, related_name="related_cart")
    total_products = models.IntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    in_order = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def products_in_cart(self):
        return [c.content_object for c in self.products.all()]

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartProduct(models.Model):

    user = models.ForeignKey("Customer", verbose_name="Покупатель", on_delete=models.CASCADE)
    cart = models.ForeignKey("Cart", verbose_name="Корзина", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")

    def __str__(self):
        return f"Продукт: {self.content_object.title}"

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Продукт корзины"
        verbose_name_plural = "Продукты корзины"


class Order(models.Model):

    customer = models.ForeignKey("Customer", verbose_name="Покупатель", related_name="orders", on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, verbose_name="Корзина", null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateField(verbose_name="Дата создания", auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderPay(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    comment = models.CharField(max_length=512, verbose_name="Комментарий")
    sum = models.DecimalField(max_digits=9, decimal_places=2)
    date_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    pay = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Оплаченный заказ"
        verbose_name_plural = "Оплаченные заказы"
