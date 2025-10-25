from django.contrib import admin
from .models import Post, Farmer, Crop, Recommendation, ImportantDate


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'location')


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'farmer', 'recommended_crop', 'date_created')


@admin.register(ImportantDate)
class ImportantDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'farmer', 'crop', 'event_type', 'date', 'end_date', 'recurrence')
    list_filter = ('event_type', 'date')
    search_fields = ('farmer__name', 'crop__name', 'notes', 'recurrence')
