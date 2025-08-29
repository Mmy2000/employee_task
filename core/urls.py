from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet,
    DepartmentViewSet,
    EmployeeViewSet,
    ProjectViewSet,
)

router = DefaultRouter()

router.register("companies", CompanyViewSet, basename="company")
router.register("departments", DepartmentViewSet, basename="department")
router.register("employees", EmployeeViewSet, basename="employee")
router.register("projects", ProjectViewSet, basename="project")


urlpatterns = [
    path("", include(router.urls)),
]
