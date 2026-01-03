from .models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password',)


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
        )
        return user




class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class loginSerializers (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','password')


        