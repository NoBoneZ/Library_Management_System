from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .serializers import BookSerializer
from .permissions import IsStaffOrReadOnly
from .mixins import IsStaffOrReadOnlyMixins
from management_system.models import Book


class ManagementSystemApiRoot(APIView):
    def get(self, request):
        return Response({
            "book": reverse("management_system_api:book_list", request=request),
        })


class BookListView(IsStaffOrReadOnlyMixins, ListCreateAPIView):
    queryset = Book.active_objects.all()
    serializer_class = BookSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]


class BookDetailView(IsStaffOrReadOnlyMixins, RetrieveUpdateDestroyAPIView):
    queryset = Book.active_objects.all()
    serializer_class = BookSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
