from rest_framework.routers import DefaultRouter
from apis import views

routers = DefaultRouter()

routers.register("v1/user", views.UserViewSet, basename="user")
routers.register("v1/login", views.LoginViewSet, basename="login")
routers.register("v1/forgot_password", views.ForgotPasswordView, basename="forgot_password")
routers.register("v1/set_password", views.SetPasswordViewSet, basename="set_password")



urlpatterns = []
urlpatterns +=routers.urls