from django.urls import path
from processor import views

app_name = "processor"

urlpatterns = [
    path("validation-block", views.CreateValidationBlockView.as_view(), name="create-validation-block"),
    path("validation", views.ValidationView.as_view(), name="validation")
]


