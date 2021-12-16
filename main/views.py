from django.shortcuts import render
from django import views
from .models import *
from django.conf import settings
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .mixins import CartMixin
from .pay import create_pay_form, payment_history_last
from django.contrib import messages
from utils import recalc_cart
import uuid
from django.core.mail import send_mail

class BaseView(CartMixin, views.View):

    def get(self,request, *args, **kwargs):
        latest_categories = Category.objects.all().order_by('-id')[:10]
        latest_products = Product.objects.all().order_by('-id')[:12]
        context = {
            "latest_products": latest_products,
            "latest_categories": latest_categories,
            "cart": self.cart
        }
        return render(request, "base.html", context)

class CategoryProductView(CartMixin, views.View):

    def get(self,request, *args, **kwargs):
        category_slug = kwargs.get('slug')
        category = Category.objects.get(slug=category_slug)
        latest_categories = Category.objects.all().order_by('-id')[:10]
        products = Product.objects.filter(category=category)
        context = {
            "category": category,
            "products": products,
            "latest_categories": latest_categories,
            "cart": self.cart
        }
        return render(request, "category_product.html", context)


class LoginView(views.View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'login.html', context)



class RegistrationView(views.View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)

class AddToCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)


        if created:
            self.cart.products.add(cart_product)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        recalc_cart(self.cart)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class DeleteFromCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)

        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CartView(CartMixin, views.View):
    def get(self, request, *args, **kwargs):
        return render(request, "cart.html", {'cart': self.cart})


class CheckOutView(CartMixin, views.View):

    def get(self,request, *args, **kwargs):
        order = Order.objects.filter(cart=self.cart).exists()
        context = {
            'cart': self.cart,
            'order': order
        }

        return render(request, "checkout.html", context)



class MakeOrderView(CartMixin, views.View):

    def post(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        self.cart.in_order = True
        self.cart.save()
        new_order = Order.objects.create(customer=customer, cart=self.cart)

        amountInteger, amountFraction = str(self.cart.final_price).split('.')
        comment = uuid.uuid4()
        url = create_pay_form(comment, amountInteger=amountInteger, amountFraction=amountFraction)
        orderpay = OrderPay.objects.create(order=new_order, comment=comment, sum=self.cart.final_price)
        context = {
            'url': str(url)
        }
        return HttpResponseRedirect(url)


class AccountView(CartMixin, views.View):
    def get(self,request,*args,**kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
        return render(request, 'account.html', {'customer': customer, 'orders': orders, 'cart': self.cart})


class ConfirmPayView(CartMixin, views.View):

    def get(self,request,*args,**kwargs):
        order_id = kwargs.get('order_id')
        order = Order.objects.filter(id=order_id).first()
        orderpay = OrderPay.objects.get(order=order)
        if orderpay.pay:
            messages.add_message(request, messages.INFO, f"Заказ от {orderpay.order.id} уже оплачен")
            return HttpResponseRedirect('/account/')
        else:
            lastpayment = payment_history_last('5','','')
            comment = str(orderpay.comment)
            for item in lastpayment['data']:
                if item.get('comment') == comment and item.get("statusText") == 'Success':
                    order.is_paid = True
                    order.save()
                    messages.add_message(request, messages.INFO,"Оплата найдена")
                    return HttpResponseRedirect('/account/')
                else:
                    messages.add_message(request, messages.INFO, "Оплата не найдена")
                    return HttpResponseRedirect('/account/')


class CategoryView(CartMixin, views.View):

    def get(self,request, *args, **kwargs):
        categories = Category.objects.all()
        latest_categories = Category.objects.all().order_by('-id')[:10]
        context = {
            "categories": categories,
            "cart": self.cart,
            'latest_categories': latest_categories
        }
        return render(request, 'category.html', context)
