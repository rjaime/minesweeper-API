from django.shortcuts import render

from rest_framework import permissions as drf_permissions
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import permissions, serializers
from .models import Match

# Create your views here.

class MatchViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [drf_permissions.IsAuthenticated]#, permissions.IsUserOwner]
    queryset = Match.objects.all()  # pylint: disable=no-member

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.UserMatchListSerializer
        elif self.action == 'create':
            return serializers.UserMatchCreateSerializer

        return serializers.UserMatchSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()  # pylint: disable=no-member
        context['user'] = self.request.user
        return context

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
