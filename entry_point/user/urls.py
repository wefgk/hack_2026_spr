from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import FirstAdminView, CreateUserView, LoginView

urlpatterns = [
    # Swagger документация
    path('schema/', SpectacularAPIView.as_view()),
    path('docs/', SpectacularSwaggerView.as_view(url='/schema/')),

    # Ваши эндпоинты
    path('auth/first-admin/', FirstAdminView.as_view()),
    path('auth/create-user/', CreateUserView.as_view()),
    path('auth/login/', LoginView.as_view()),
]