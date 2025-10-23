from django.urls import path
from .views import (
    PostListCreateView, 
    crop_recommendation_view,
    crop_info_view,
    crops_list_view,
    price_forecast_view,
    FarmerListCreateView,
    FarmerDetailView,
    recommendation_history_view,
    farmer_register_view,
    farmer_login_view
)

urlpatterns = [
    # Posts
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    
    # Crop Recommendation
    path('recommend/', crop_recommendation_view, name='crop-recommendation'),
    
    # Crop Information
    path('crops/', crops_list_view, name='crops-list'),
    path('crops/<int:crop_id>/', crop_info_view, name='crop-info'),
    
    # Price Forecast
    path('forecast/<int:crop_id>/', price_forecast_view, name='price-forecast'),
    
    # Farmer Management
    path('farmers/', FarmerListCreateView.as_view(), name='farmer-list-create'),
    path('farmers/<int:pk>/', FarmerDetailView.as_view(), name='farmer-detail'),
    path('farmers/<int:farmer_id>/recommendations/', recommendation_history_view, name='recommendation-history'),
    
    # Authentication
    path('auth/register/', farmer_register_view, name='farmer-register'),
    path('auth/login/', farmer_login_view, name='farmer-login'),
]
