from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from .models import ApplicationExtension, ApplicationContentType
from processor.serializers import ValidatorBlockSerializer
from .serializers import ApplicationContentTypeSerializer, ApplicationExtensionSerializer

# Create your views here.


class GetView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            query: str = request.GET.get("search", None)

            if not query:
                return Response({"detail": "'search' is required"}, status=HTTP_400_BAD_REQUEST)

            if query.lower() == 'content-types':
                content_sets = ApplicationContentType.objects.all()
                content_serializer = ApplicationContentTypeSerializer(content_sets, many=True).data
                return Response({"detail": content_serializer})

            if query.lower() == 'extensions':
                content_sets = ApplicationExtension.objects.all()
                content_serializer = ApplicationExtensionSerializer(content_sets, many=True).data
                return Response({"detail": content_serializer})

            return Response({"detail": "Something went wrong. "}, status=HTTP_400_BAD_REQUEST)
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)
