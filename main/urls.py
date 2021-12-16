from django.urls import path
from .views import (
    BaseView,
    CategoryProductView,
    LoginView,
    RegistrationView,
    AddToCartView,
    DeleteFromCartView,
    CartView,
    CheckOutView,
    MakeOrderView,
    AccountView,
    ConfirmPayView,
    CategoryView
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", BaseView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(next_page="/"), name="logout"),
    path('cart/', CartView.as_view(), name="cart"),
    path('checkout/', CheckOutView.as_view(), name="checkout"),
    path('make-order/', MakeOrderView.as_view(), name="make_order"),
    path('account/', AccountView.as_view(), name="account"),
    path('category/', CategoryView.as_view(), name="category"),
    path('confirm-pay/<int:order_id>/', ConfirmPayView.as_view(), name="confirm_pay"),



    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name="add_to_cart"),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name="delete_from_cart"),
    path("category/<str:slug>/", CategoryProductView.as_view(), name="category_product"),
]
