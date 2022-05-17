from django.contrib import admin
from student.models import User
from student.models import ForgotPassword
# Register your models here.
admin.site.register(User)
admin.site.register(ForgotPassword)
