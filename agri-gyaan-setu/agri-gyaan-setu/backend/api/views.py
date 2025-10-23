from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from .ml_service import predict_crop
from .models import Post, Farmer, Crop, Recommendation
from .serializers import PostSerializer, FarmerSerializer, CropSerializer, RecommendationSerializer

# --- ML Crop Recommendation API ---
@api_view(['POST'])
def crop_recommendation_view(request):
    features = request.data.get('features')  # Expecting a list of input features
    if features is None:
        return Response({'error': 'Missing features in request.'}, status=400)
    recommended_crop = predict_crop(features)
    return Response({'recommended_crop': recommended_crop})

# --- Crop Information API ---
@api_view(['GET'])
def crop_info_view(request, crop_id):
    try:
        crop = Crop.objects.get(id=crop_id)
        serializer = CropSerializer(crop)
        return Response(serializer.data)
    except Crop.DoesNotExist:
        return Response({'error': 'Crop not found'}, status=404)

@api_view(['GET'])
def crops_list_view(request):
    crops = Crop.objects.all()
    serializer = CropSerializer(crops, many=True)
    return Response(serializer.data)

# --- Price Forecast API (Mock data for now) ---
@api_view(['GET'])
def price_forecast_view(request, crop_id):
    try:
        crop = Crop.objects.get(id=crop_id)
        # Mock price forecast data - replace with real data source
        forecast_data = {
            'crop_name': crop.name,
            'current_price': 2500,  # Mock current price
            'msp': 2200,  # Mock MSP
            'trend': 'Increasing',
            'forecast': {
                'month_1': 2600,
                'month_2': 2700,
                'month_3': 2650,
                'month_4': 2800,
                'month_5': 2750,
                'month_6': 2900
            }
        }
        return Response(forecast_data)
    except Crop.DoesNotExist:
        return Response({'error': 'Crop not found'}, status=404)

# --- Farmer Management APIs ---
class FarmerListCreateView(generics.ListCreateAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer

class FarmerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer

# --- Recommendation History API ---
@api_view(['GET'])
def recommendation_history_view(request, farmer_id):
    try:
        farmer = Farmer.objects.get(id=farmer_id)
        recommendations = Recommendation.objects.filter(farmer=farmer).order_by('-date_created')
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    except Farmer.DoesNotExist:
        return Response({'error': 'Farmer not found'}, status=404)

# --- Authentication APIs ---
@api_view(['POST'])
def farmer_register_view(request):
    serializer = FarmerSerializer(data=request.data)
    if serializer.is_valid():
        farmer = serializer.save()
        return Response({
            'message': 'Farmer registered successfully',
            'farmer_id': farmer.id,
            'name': farmer.name
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def farmer_login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        farmer = Farmer.objects.get(email=email)
        # For now, accept any password for existing farmers (development only)
        # In production, you should use proper password hashing
        return Response({
            'message': 'Login successful',
            'farmer_id': farmer.id,
            'name': farmer.name,
            'email': farmer.email
        })
    except Farmer.DoesNotExist:
        return Response({'error': 'Farmer not found. Please register first.'}, status=status.HTTP_404_NOT_FOUND)

# --- Post List/Create API using DRF generics ---
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
