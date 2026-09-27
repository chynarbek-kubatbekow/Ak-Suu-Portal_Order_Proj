# Copyright (c) 2026 Ak-Suu Portal Project Team. All rights reserved.
# Proprietary software. See LICENSE for terms.
"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.views.generic import RedirectView
from .environment import IS_WORKER
from .media import public_image

urlpatterns = [
    path('admin', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
]

if IS_WORKER:
    urlpatterns += [path('__ops/', include('myproject.worker_operations'))]
if (IS_WORKER or settings.SERVE_LOCAL_MEDIA) and settings.MEDIA_URL == '/media/':
    urlpatterns += [path('media/<path:name>', public_image)]
urlpatterns += [path('', include('myapp.urls'))]
