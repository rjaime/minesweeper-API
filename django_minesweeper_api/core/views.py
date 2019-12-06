from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views import View

from rest_framework import (
    exceptions as drf_exceptions,
    permissions as drf_permissions,
)
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
        x, y = self.extract_coords(request.data)

        try:
            match = Match.objects.get(id=pk)  # pylint: disable=no-member
        except Match.DoesNotExist:
            return Response(
                {'message': _("Match id {} not found.".format(pk))},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            game_status, cells_revealed = match.reveal(x, y)
        except Exception as ex:
            raise drf_exceptions.APIException(str(ex))

        response_data = {
            'target': [x, y],
            'game_status': game_status,
            'cells': cells_revealed,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        x, y = self.extract_coords(request.data)

        try:
            match = Match.objects.get(id=pk)  # pylint: disable=no-member
        except Match.DoesNotExist:
            return Response(
                {'message': _("Match id {} not found.".format(pk))},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            valid, cells_revealed = match.flag(x, y)
        except Exception as ex:
            raise drf_exceptions.APIException(str(ex))

        response_data = {
            'target': [x, y],
            'game_status': '0',
            'cells': cells_revealed,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def extract_coords(self, req_data):
        x = req_data.get('x', None)
        
        if x is None:
            raise drf_exceptions.ValidationError(_("'x' value is missing."))

        y = req_data.get('y', None)
        
        if y is None:
            raise drf_exceptions.ValidationError(_("'y' value is missing."))

        if not isinstance(x, int):
            raise drf_exceptions.ValidationError(_("'x' must be integer"))

        if not isinstance(y, int):
            raise drf_exceptions.ValidationError(_("'y' must be integer"))

        if x < 0:
            raise drf_exceptions.ValidationError(_("'x' must be zero or greater."))

        if y < 0:
            raise drf_exceptions.ValidationError(_("'y' must be zero or greater."))

        return x, y


class GameView(View):
    def get(self, request, match_id):
        context = {'match_id': match_id}
        return render(request, 'game.html', context)
