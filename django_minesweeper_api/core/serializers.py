from django.core.validators import ValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .models import Board, Match


class UserBoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = ('match', 'rows', 'cols', 'cells')
        extra_kwargs = {
            'match': {"read_only": True},
            'rows': {'read_only': True},
            'cols': {'read_only': True},
            'cells': {'read_only': True},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['cells'] = instance.get_cells_representation_for_user()
        return rep


class UserMatchSerializer(serializers.ModelSerializer):
    board = UserBoardSerializer()

    class Meta:
        model = Match
        fields = ('id', 'board', 'created_at', 'last_action_at')
        extra_kwargs = {
            'board': {'read_only': True},
            'created_at': {'read_only': True},
            'last_action_at': {'read_only': True},
        }


class UserMatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'created_at', 'last_action_at')
        extra_kwargs = {
            'created_at': {'read_only': True},
            'last_action_at': {'read_only': True},
        }


class UserMatchCreateSerializer(serializers.ModelSerializer):
    rows = serializers.IntegerField(required=True, write_only=True)
    cols = serializers.IntegerField(required=True, write_only=True)
    mines = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = Match
        fields = ('rows', 'cols', 'mines')
        extra_kwargs = {
            'rows': {'write_only': True},
            'cols': {'write_only': True},
            'mines': {'write_only': True},
        }

    def validate(self, data):
        # user
        user = self.context.get('user', None)
        if user is None:
            raise ValueError("User in context is required.")

        # rows
        if not data['rows'] > 0:
            raise serializers.ValidationError(_("Rows must be greater than 0."))

        # cols
        if not data['cols'] > 0:
            raise serializers.ValidationError(_("Cols must be greater than 0."))

        # rows, cols
        if data['rows'] == 1 and data['cols'] == 1:
            raise serializers.ValidationError(_("Size 1x1 is not valid."))

        # mines
        if not data['mines'] > 0:
            raise serializers.ValidationError(_("Mines must be greater than 0."))

        total_cells = data['rows'] * data['cols']

        if data['mines'] >= total_cells:
            raise serializers.ValidationError(_("Mines number must be lower than total number of cells."))

        return data

    def create(self, validated_data):
        user = self.context['user']
        rows = validated_data['rows']
        cols = validated_data['cols']
        mines = validated_data['mines']

        match = Match.create(user, rows, cols, mines)

        return match

    def to_representation(self, instance):
        return UserMatchSerializer(instance).data
