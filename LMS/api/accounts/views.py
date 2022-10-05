from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from .serializers import MembersSerializer, WalletSerializer
from accounts.models import Members, Wallet
from ..management_system.mixins import IsStaffOrReadOnlyMixins


class AccountsApiRoot(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            "members": reverse("accounts_api:members_list_create", request=request),
            "wallet": reverse("accounts_api:wallet_list_create", request=request)
        })


class MemberListCreateView(IsStaffOrReadOnlyMixins, ListCreateAPIView):
    serializer_class = MembersSerializer
    queryset = Members.active_objects.all()


class WalletListCreateView(IsStaffOrReadOnlyMixins, ListCreateAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
