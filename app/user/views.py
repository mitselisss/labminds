# user/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"username": user.username},
            status=status.HTTP_201_CREATED
        )
