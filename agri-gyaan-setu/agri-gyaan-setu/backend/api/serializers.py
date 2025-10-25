from rest_framework import serializers
from .models import Post, Farmer, Crop, Recommendation
from .models import Post, Farmer, Crop, Recommendation, ImportantDate
from django.contrib.auth.hashers import make_password

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content']

class FarmerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Farmer
        fields = ['id', 'name', 'email', 'location', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['id', 'name', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']

class RecommendationSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.name', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'farmer', 'farmer_name', 'recommended_crop', 'date_created']


class ImportantDateSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.name', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)

    class Meta:
        model = ImportantDate
        fields = ['id', 'farmer', 'farmer_name', 'crop', 'crop_name', 'event_type', 'date', 'end_date', 'recurrence', 'notes', 'created_at']

    def validate_event_type(self, value):
        """Coerce unknown event_type values to 'other' so badly-formed client payloads
        don't raise ValidationError. We also preserve the original text into notes
        during create() if notes is not provided.
        """
        valid = {c[0] for c in getattr(self.Meta.model, 'EVENT_TYPES', [])}
        return value if value in valid else 'other'

    def create(self, validated_data):
        # If the client sent a non-standard event_type and didn't provide notes,
        # preserve the original event_type string into notes so the user title isn't lost.
        orig_event_type = None
        try:
            orig_event_type = self.initial_data.get('event_type')
        except Exception:
            orig_event_type = None
        if orig_event_type and validated_data.get('event_type') == 'other' and not validated_data.get('notes'):
            validated_data['notes'] = orig_event_type
        return super().create(validated_data)