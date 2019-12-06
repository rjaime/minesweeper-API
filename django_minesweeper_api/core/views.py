from django.shortcuts import render

from rest_framework import permissions as drf_permissions
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import permissions, serializers

# Create your views here.

class MatchesViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsUserOwner]
    serializer_class = serializers.UserMatchSerializer

    @action(detail=True, methods=['post'])
    def reveal(self, request, pk=None):
        response_data = {
            'target': [0, 0],
            'cells': {},
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        response_data = {
            'target': [0, 0],
            'cells': {},
        }
        return Response(response_data, status=status.HTTP_200_OK)
