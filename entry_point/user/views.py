from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .models import User, UserDevice
from .serializers import LoginResponseSerializer, UserSerializer, LoginSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

# cоздание первого админа !!!бд должна быть пуста!!!
@extend_schema(
    summary="Создание первого администратора",
    description="Создает первого пользователя с правами администратора. Доступно только если база данных пуста",
    request=UserSerializer,
    responses={
        201: OpenApiResponse(description="Администратор успешно создан"),
        403: OpenApiResponse(description="Ошибка: администратор уже существует"),
        400: OpenApiResponse(description="Ошибка валидации данных"),
    },
    tags=["Admin"])
class FirstAdminView(CreateAPIView):
    serializer_class = UserSerializer


    def create(self, request, *args, **kwargs):
        if User.objects.filter(is_admin=True).exists():
            return Response({"detail": "администратор уже существует. Используйте вход."},
                             status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        data['is_admin'] = True
        
        user = User.objects.create_user(
            email=data['email'],
            name=data['name'],
            surname=data['surname'],
            patronymic=data.get('patronymic'),
            password=data['password'],
            is_admin=True
        )
        
        return Response({"message": "Первый админ создан", "email": user.email}, status=status.HTTP_201_CREATED)

# 2. Создание пользователей
@extend_schema(
    summary="Создание нового пользователя",
    description="Создает нового пользователя. Доступно только авторизованным администраторам.",
    request=UserSerializer,
    responses={
        201: OpenApiResponse(description="Пользователь успешно создан"),
        401: OpenApiResponse(description="Ошибка: не авторизован"),
        400: OpenApiResponse(description="Ошибка валидации данных"),
        403: OpenApiResponse(description="Ошибка: недостаточно прав"),
    },
    tags=["Admin"]
    )
class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response({"detail": "Только администраторы могут создавать пользователей."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data

        if 'is_admin' not in data:
            data['is_admin'] = False
            
        user = User.objects.create_user(
            email=data['email'],
            name=data['name'],
            surname=data['surname'],
            patronymic=data.get('patronymic'),
            password=data['password'],
            is_admin=data.get('is_admin', False),
        )
        
        return Response({"message": "Пользователь создан", "id": user.id}, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    @extend_schema(
    summary="Вход в систему",
    description="Аутентификация пользователя по email и паролю. Создает запись устройства и возвращает данные пользователя вместе с ключом устройства",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Успешный вход", response=LoginResponseSerializer),
        401: OpenApiResponse(description="Ошибка: неверный email или пароль"),
        400: OpenApiResponse(description="Ошибка валидации данных"),
    },
    tags=["User"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        device_name = serializer.validated_data.get('device_name')

        user = authenticate(username=email, password=password)
        
        if not user:
            return Response({"detail": "Неверный email или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

        device=UserDevice.objects.create(user=user, device_name=device_name)

        return Response({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "device_code":device.key,
                "surname": user.surname,
                "is_admin": user.is_admin
        }, status=status.HTTP_200_OK)