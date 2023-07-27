from django.urls import path
from .views import UsersView, TasksView, LoginView

urlpatterns = [
    path('users/', UsersView.as_view()),
    path('users/<int:pk>/', UsersView.as_view()),
    path('tasks/', TasksView.as_view()),
    path('tasks/<int:pk>/', TasksView.as_view()),

    path('login/', LoginView.as_view()),
]
