from django.forms.fields import FileField
from rest_framework import serializers

from .models import Worker, Position

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

class PositionImportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        exclude = ('pk', 'id')


class WorkerSerializerRead(serializers.ModelSerializer):

    position = PositionSerializer(read_only=True)

    class Meta:
        model = Worker
        fields = ("id", "first_name", "middle_name", "last_name", "position", "is_active") #remove hired_date

class WorkerSerializerWrite(serializers.ModelSerializer):

    position = PositionSerializer()

    class Meta:
        model = Worker
        fields = "__all__"


    def update(self, instance, validated_data):
        pos = validated_data.get('position')
        pos_name = pos['name']
        new_pos = Position.objects.get(name=pos_name)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.position = new_pos
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.hired_date = validated_data.get('hired_date', instance.hired_date)
        instance.created_by = instance.created_by
        instance.save()
        return instance

class WorkerImportWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Worker
        fields = ("first_name","middle_name","last_name","email", "is_active", "hired_date", "created_by","is_deleted", "deleted_at")

class ExcelFileSerializer(serializers.Serializer):
    file = serializers.FileField(allow_empty_file=False)