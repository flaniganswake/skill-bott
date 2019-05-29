from django.urls import path
from .views import view_page


urlpatterns = [
    path('<str:title>', view_page, name='static_cms.views.view_page')
]
