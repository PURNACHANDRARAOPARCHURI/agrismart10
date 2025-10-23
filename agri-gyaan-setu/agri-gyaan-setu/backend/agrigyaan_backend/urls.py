from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    
    # Serve static HTML files
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('index.html', TemplateView.as_view(template_name='index.html'), name='home-html'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('dashboard.html', TemplateView.as_view(template_name='dashboard.html'), name='dashboard-html'),
    path('crop-info/', TemplateView.as_view(template_name='crop_info.html'), name='crop-info'),
    path('crop_info.html', TemplateView.as_view(template_name='crop_info.html'), name='crop-info-html'),
    path('crop-recommend/', TemplateView.as_view(template_name='crop_recommend.html'), name='crop-recommend'),
    path('crop_recommend.html', TemplateView.as_view(template_name='crop_recommend.html'), name='crop-recommend-html'),
    path('price-forecast/', TemplateView.as_view(template_name='price_forecast.html'), name='price-forecast'),
    path('price_forecast.html', TemplateView.as_view(template_name='price_forecast.html'), name='price-forecast-html'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('signup.html', TemplateView.as_view(template_name='signup.html'), name='signup-html'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])