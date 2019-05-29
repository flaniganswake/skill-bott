from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView
from django.views.static import serve
from rest_framework import routers, serializers, viewsets
import views
import api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='login.html'),
         name="login"),
    path('accounts/login/', LoginView.as_view(template_name='login.html'),
         name="login"),
    path('logout/', LogoutView.as_view(template_name='home.html'),
         name="logout"),

    path('certificate/', views.certificate,
         name='views.certificate'),
    path('start_demo/', views.start_demo,
         name='views.start_demo'),

    path('interests_inventory/<str:start>/', views.interests_inventory,
         name='views.interests_inventory'),
    path('interests_analysis/', views.interests_analysis,
         name='views.interests_analysis'),
    path('interests_summary/', views.interests_summary,
         name='views.interests_summary'),
    path('interests_instructions/', views.interests_instructions,
         name='views.interests_instructions'),

    path('skills_inventory/', views.skills_inventory,
         name='views.skills_inventory'),
    path('skills_analysis/', views.skills_analysis,
         name='views.skills_analysis'),
    path('skills_summary/', views.skills_summary,
         name='views.skills_summary'),

    path('skills_inventory/', views.values_inventory,
         name='views.values_inventory'),
    path('skills_analysis/', views.values_analysis,
         name='views.values_analysis'),
    path('skills_summary/', views.values_summary,
         name='views.values_summary'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('cms/', include('static_cms.urls')),

    # path('users/', views.home, name='home'),
    # ?? called after new user registration
]

urlpatterns += [
    # path('', include(router.urls)),
    path('api/auth/', api.auth_user,
         name='api.auth-user'),
    path('api-auth/', include('rest_framework.urls',
         namespace='rest_framework')),
    path('api/register/', api.register,
         name='api.register'),
    path('api/', api.api_root,
         name='api.api-root'),
    path('api/inventory/', api.inventory_list,
         name='api.inventory-list'),
    path('api/inventory/<int:pk>/', api.inventory_detail,
         name='api.inventory-detail'),
    path('api/category/', api.category_list,
         name='api.category-list'),
    path('api/category/<int:pk>/', api.category_detail,
         name='api.category-detail'),
    path('api/topic/', api.topic_list,
         name='api.topic-list'),
    path('api/topic/<int:pk>/', api.topic_detail,
         name='api.topic-detail'),
    path('api/answer/', api.answer_list,
         name='api.answer-list'),
    path('api/post-answer', api.answer_create,
         name='api.answer-create'),
    path('api/choice/', api.choice_list,
         name='api.choice-list'),
    path('api/choice/<int:pk>/', api.choice_detail,
         name='api.choice-detail'),
    path('api/scores/', api.scores_list,
         name='api.scores-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('500/',
             TemplateView.as_view(template_name='500.html'),
             name='500_error'),
        path('404/',
             TemplateView.as_view(template_name='404.html'),
             name='404_error')
    ]