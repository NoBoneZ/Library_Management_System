from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def Lms_api_root(request):
    return Response({
            "accounts": reverse("accounts_api:accounts_root", request=request),
            "management_system": reverse("management_system_api:api_root", request=request)
    })
