from rest_framework import serializers
from .models import Worker, Position

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

class WorkerSerializer(serializers.ModelSerializer):

    position = PositionSerializer(read_only=True)

    class Meta:
        model = Worker
        fields = ("id", "first_name", "middle_name", "last_name", "position", "is_active")
        # fields = "__all__"

