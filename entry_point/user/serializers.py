from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'surname', 'patronymic', 'password', 'is_admin')
        read_only_fields = ('id',)

    def create(self, validated_data):

        password = validated_data.pop('password')
        
        user = User.objects.create_user(password=password, **validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    device_name = serializers.CharField(required=False, allow_blank=True, default="Unknown")


#для swagger 
#=====================================================================

class LoginResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField()
    surname = serializers.CharField()
    is_admin = serializers.BooleanField()
    device_code = serializers.CharField() # Или UUIDField, если key это UUID