from django.urls import path

from restaurant.views.menu_views import MenuCreateView
from restaurant.views.menu_views import (
    AllRestaurantsCurrentDayMenuView,
)
from restaurant.views.signup_views import RestaurantSignUpView


urlpatterns = [
    path("signup/", RestaurantSignUpView.as_view(), name="restaurant-signup"),
    path("menu/", MenuCreateView.as_view(), name="menu-create"),
    path(
        "menu/today/",
        AllRestaurantsCurrentDayMenuView.as_view(),
        name="all-restaurants-current-day-menu",
    ),
]
