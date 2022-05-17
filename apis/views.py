from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from student.models import User
from student.models import ForgotPassword
from apis.serializers import UserSerializer
from apis.serializers import LoginSerializer
from rest_framework.authtoken.models import Token
from apis.mailer import Mailer
from django.utils import timezone
from django.shortcuts import render

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(id=serializer.data["id"])
            user.set_password(request.data["password"])
            user.save()
            return Response({"data":self.serializer_class(user).data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        return Response({"data":self.serializer_class(self.get_queryset(), many=True).data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if User.objects.filter(id=kwargs.get("pk")).exists():
            user = User.objects.get(id=kwargs.get("pk"))
            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":self.serializer_class(user).data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"data":"User does not exists."}, status=status.HTTP_200_OK)  

    def retrieve(self, request, *args, **kwargs):
        if User.objects.filter(id=kwargs.get("pk")).exists():
            user = User.objects.get(id=kwargs.get("pk"))
            return Response({"data":self.serializer_class(user).data}, status=status.HTTP_200_OK)   
        return Response({"data":"User does not exists."}, status=status.HTTP_200_OK)  

class LoginViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["user"])    
            if Token.objects.filter(user=user).exists():
                token = Token.objects.get(user=user)
                token.delete()
            token_key = Token.objects.create(user=user)
            data = UserSerializer(user).data
            data["token"] = token_key.key
            return Response({"data":data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        if User.objects.filter(email=request.data["email"]).exists():
            user = User.objects.get(email=request.data["email"])
            forgot_instance = ForgotPassword.objects.create(user=user)
            mailer = Mailer(email=request.data["email"], host=request.get_host(), hash=forgot_instance.hash)
            mailer_response = mailer()
            return Response({"message":"Reset link send to the register email."}, status=status.HTTP_200_OK)
        return Response({"message":"User with this email does not exists."}, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        hash = self.request.query_params.get("q", None)
        password = request.data.get("password", None)
        confirm_password = request.data.get("confirm_password", None)
        if password == confirm_password:
            forgot_instance = ForgotPassword.objects.get(hash=hash)
            user_instance = User.objects.get(email=forgot_instance.user)
            user_instance.set_password(password)
            user_instance.save()
            forgot_instance.is_used=True
            forgot_instance.used_at = timezone.now()
            forgot_instance.save()
            return render(request, "success.html")
        else:
            return Response({"message":"Password and confirm password are not matched."}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        hash = self.request.query_params.get("q", None)
        forgot_instance = ForgotPassword.objects.get(hash=hash)
        if forgot_instance.is_used==False and forgot_instance.expire_at > timezone.now():
            return render(request, "set_password.html", {'hash':hash})
        else:
            return render(request, "link_expire.html")