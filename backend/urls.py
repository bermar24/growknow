"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

# Keep project-level routing small. App modules should provide their own URL patterns.

urlpatterns = [
    path('admin/', admin.site.urls),
    # Mount the news API at /api/news/ (so articles will be at /api/news/articles/)
    path('api/news/', include('backend.news.urls')),
]
