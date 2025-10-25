from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import generics, status
from .ml_service import predict_crop
from .models import Post, Farmer, Crop, Recommendation, ImportantDate
from .serializers import PostSerializer, FarmerSerializer, CropSerializer, RecommendationSerializer, ImportantDateSerializer
from django.contrib.auth.hashers import check_password
from .weather import geocode_location, fetch_short_forecast
from . import price_model
from pathlib import Path
from django.utils.dateparse import parse_date

BASE_DIR = Path(__file__).resolve().parents[2]

# --- ML Crop Recommendation API ---
@csrf_exempt
@api_view(['POST'])
def crop_recommendation_view(request):
    features = request.data.get('features')  # Expecting a list of input features
    if features is None:
        return Response({'error': 'Missing features in request.'}, status=400)

    # Enrich with weather data if location provided
    location = request.data.get('location')
    if location:
        lat, lon = geocode_location(location)
        weather = fetch_short_forecast(lat, lon)
        # Append weather features (temperature, humidity, rainfall) to features
        try:
            features = list(features) + [weather.get('temperature', 25.0), weather.get('humidity', 70.0), weather.get('rainfall', 0.0)]
        except Exception:
            pass

    recommended_crop = predict_crop(features)

    # Mock additional ML outputs — replace with your model outputs if available
    expected_yield = "3.2 tonnes/hectare"  # Placeholder: compute from model if available
    predicted_price = "₹ 24/kg"
    # Mock 6-month price forecast (replace with price-prediction model)
    forecast = {
        'month_1': 24,
        'month_2': 25,
        'month_3': 23,
        'month_4': 26,
        'month_5': 27,
        'month_6': 28,
    }

    # Determine best selling month (highest forecasted price)
    best_month_index = max(range(1,7), key=lambda i: forecast[f'month_{i}'])
    best_selling_month = f'Month {best_month_index}'

    # Optionally persist recommendation if farmer_id provided
    farmer_id = request.data.get('farmer_id')
    if farmer_id:
        try:
            farmer = Farmer.objects.get(id=farmer_id)
            Recommendation.objects.create(farmer=farmer, recommended_crop=recommended_crop)
        except Farmer.DoesNotExist:
            # ignore saving if farmer not found
            pass

    return Response({
        'recommended_crop': recommended_crop,
        'expected_yield': expected_yield,
        'predicted_price': predicted_price,
        'best_selling_month': best_selling_month,
        'forecast': forecast
    })

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
        # Try to load an existing price model
        model = price_model.load_model()
        dataset_path = BASE_DIR / 'frontend' / 'assets' / 'dataset1.csv'
        if model is None and dataset_path.exists():
            try:
                price_model.train_and_save_model(str(dataset_path))
                model = price_model.load_model()
            except Exception:
                model = None

        # Default base price / msp per crop (per-quintal values used for demo)
        base_prices = {
            'Rice': 2500,
            'Wheat': 2200,
            'Maize': 1800,
            'Sugarcane': 1500,
            'Cotton': 3000,
            'Millet': 1600,
            'Barley': 1700,
            'Sorghum': 1400,
            'Soybean': 2600,
            'Potato': 1200
        }
        current_price = base_prices.get(crop.name, 2000)
        msp = int(current_price * 0.88)

        # Predict relative change using the generic price model and scale by crop base
        raw_forecast = price_model.predict_next_months(6) if model is not None else [0,0,0,0,0,0]
        if raw_forecast and any(raw_forecast):
            # If model returns absolute prices, scale to crop; otherwise treat as relative and add to base
            forecast_vals = []
            for v in raw_forecast:
                try:
                    fv = float(v)
                except Exception:
                    fv = 0.0
                # If model's numbers look like small values, treat them as relative deltas.
                # Scale deltas proportionally to the crop's current price for clearer differences.
                if abs(fv) < 1000:
                    scaled = int(round(current_price * (1 + (fv / max(1.0, current_price)))))
                    forecast_vals.append(scaled)
                else:
                    forecast_vals.append(int(round(fv)))
        else:
            # Fallback synthetic forecast slight variation around base price
            forecast_vals = [int(current_price * (1 + r)) for r in [0.03,0.04,0.02,0.05,0.035,0.06]]

        # If forecast_vals are all identical, nudge each month slightly to avoid identical values
        if len(set(forecast_vals)) == 1:
            base = forecast_vals[0]
            forecast_vals = [int(base * (1 + d)) for d in [0.02, 0.04, 0.01, 0.05, 0.03, 0.06]]

        forecast = {
            f'month_{i+1}': int(round(forecast_vals[i])) if i < len(forecast_vals) else 0
            for i in range(6)
        }

        # Simple trend heuristic
        trend = 'Stable'
        if forecast_vals and forecast_vals[-1] > forecast_vals[0]:
            trend = 'Increasing'
        elif forecast_vals and forecast_vals[-1] < forecast_vals[0]:
            trend = 'Decreasing'

        forecast_data = {
            'crop_name': crop.name,
            'current_price': current_price,
            'msp': msp,
            'trend': trend,
            'forecast': forecast
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
        # Verify hashed password
        if farmer.password and check_password(password, farmer.password):
            return Response({
                'message': 'Login successful',
                'farmer_id': farmer.id,
                'name': farmer.name,
                'email': farmer.email
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except Farmer.DoesNotExist:
        return Response({'error': 'Farmer not found. Please register first.'}, status=status.HTTP_404_NOT_FOUND)

# --- Post List/Create API using DRF generics ---
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


# --- ImportantDate (Calendar) APIs ---
@method_decorator(csrf_exempt, name='dispatch')
class ImportantDateListCreateView(generics.ListCreateAPIView):
    serializer_class = ImportantDateSerializer

    # Add a small debug hook for development to log create payloads. This
    # helps diagnose whether POSTs are reaching the server and what the
    # payload looks like. In production you would remove this.
    def create(self, request, *args, **kwargs):
        try:
            # log to server console
            print('ImportantDate create request body:', request.body)
        except Exception:
            pass
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = ImportantDate.objects.all()
        # filter by farmer (optional)
        farmer_id = self.request.query_params.get('farmer_id')
        if farmer_id:
            qs = qs.filter(farmer__id=farmer_id)

        # Optionally accept a start/end range (preferred) or month/year parameters
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start and end:
            s = parse_date(start)
            e = parse_date(end)
            if s and e:
                qs = qs.filter(date__gte=s, date__lte=e)
                return qs.order_by('date')

        # filter by month/year (fallback) to populate calendar month view
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            try:
                m = int(month)
                y = int(year)
                qs = qs.filter(date__year=y, date__month=m)
            except ValueError:
                pass

        return qs.order_by('date')


class ImportantDateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImportantDate.objects.all()
    serializer_class = ImportantDateSerializer


@api_view(['GET'])
def weather_view(request):
    """Simple proxy to the backend weather helper.
    Accepts either ?lat=..&lon=.. or ?location=CityName and returns the
    short forecast dict produced by fetch_short_forecast.
    """
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    location = request.query_params.get('location')

    if lat and lon:
        try:
            latf = float(lat); lonf = float(lon)
        except Exception:
            return Response({'error': 'Invalid lat/lon'}, status=400)
        data = fetch_short_forecast(latf, lonf)
        return Response(data)

    if location:
        latlon = geocode_location(location)
        if latlon == (None, None):
            return Response({'error': 'Location not found or API key not configured'}, status=400)
        data = fetch_short_forecast(latlon[0], latlon[1])
        return Response(data)

    return Response({'error': 'Provide lat/lon or location parameter'}, status=400)
