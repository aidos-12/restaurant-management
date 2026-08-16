from django.contrib import admin
from django.urls import include, path

from users.views import (
    home,
    register,
    login_view,
    logout_view,
    profile,
    order_history,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    # Главная
    path("", home, name="home"),

    # Аутентификация
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Профиль
    path("profile/", profile, name="profile"),

    # Клиентская часть
    path("menu/", include("shop.urls")),

    # Бронирования
    path("reservations/", include("reservations.urls")),

    # Панель сотрудника
    path("employee/orders/", include("orders.urls")),

    # История заказов клиента
    path("orders/", order_history, name="order_history"),
]