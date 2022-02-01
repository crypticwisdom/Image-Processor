from django.urls import path
from . import views

app_name = 'country'
urlpatterns = [
    path('', views.country_view),
    path('countries/', views.country_view),
    path('create-states/', views.create_states),
    path('states/', views.GetStatesView.as_view()),
    path('get-locality/', views.GetLocalityView.as_view()),
]
