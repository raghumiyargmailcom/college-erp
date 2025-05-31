from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('controll.urls')),  # Controll app URLs
    path('student/', include(('student.urls', 'student'), namespace='student')),
        # Student app with namespace
    path('HOD/', include(('HOD.urls', 'HOD'), namespace='HOD')),  # HOD app with namespace
    path('faculty/', include(('faculty.urls', 'faculty'), namespace='faculty')),  # ✅ Faculty app with namespace
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
