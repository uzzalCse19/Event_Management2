from django.contrib import admin
from django.urls import path, include
from Event.views import EventListView
from core.views import no_permission
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar import urls as debug_toolbar_urls  # ইম্পোর্ট ঠিক করুন

urlpatterns = [
    path('', EventListView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('events/', include('Event.urls')),
    path('users/', include('users.urls')),
    path('no-permission/', no_permission, name='no-permission'),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar_urls)),  # Debug toolbar URL
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)