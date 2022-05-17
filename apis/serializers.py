from rest_framework.serializers import ModelSerializer
from student.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate

class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)

        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                data["user"]=user
                return data
            else:
                raise serializers.ValidationError("Unable to login with this corredentials.")
        else:
            raise serialzer.ValidationError("Username and password fields are required.")