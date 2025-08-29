from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reviews.views import EmployeeReviewViewSet

router = DefaultRouter()

router.register("reviews", EmployeeReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
]
