from django.shortcuts import render
from .serializers import SignUpSerializer
from .models import User
from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView

# Create your views here.

class CreateUserApiView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

    
