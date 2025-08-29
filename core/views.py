# core/views.py
from rest_framework import viewsets, mixins, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Company, Department, Employee, Project
from .serializers import (
    CompanySerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    ProjectSerializer,
)
from config.response import CustomResponse
from config.pagination import CustomPagination
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

class BaseRBACPermission(permissions.IsAuthenticated):
    # can extend for create/update/delete checks per role
    pass


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [BaseRBACPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    pagination_class = CustomPagination
    ordering = ["created_at"]

    def get_queryset(self):
        qs = Company.objects.annotate(
            departments_count=Count("departments", distinct=True),
            employees_count=Count("employees", distinct=True),
            projects_count=Count("projects", distinct=True),
        )
        user = self.request.user
        if user.role == "ADMIN":
            return qs
        if user.company_id:
            return qs.filter(id=user.company_id)
        return qs.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data, status=200)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            # add pagination metadata
            pagination_data = self.paginator.get_pagination_meta()

            return CustomResponse(
                data=serializer.data,
                status=200,
                pagination=pagination_data,
            )

        # if no pagination
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data, status=200)


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [BaseRBACPermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["company"]
    search_fields = ["name"]
    ordering_fields = ["name"]
    pagination_class = CustomPagination
    ordering = ["created_at"]

    def get_queryset(self):
        qs = Department.objects.annotate(
            employees_count=Count("employees", distinct=True),
            projects_count=Count("projects", distinct=True),
        )
        user = self.request.user
        if user.role == "ADMIN":
            return qs
        if user.company_id:
            return qs.filter(company_id=user.company_id)
        return qs.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data, status=200)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            pagination_data = self.paginator.get_pagination_meta()

            return CustomResponse(
                data=serializer.data,
                status=200,
                pagination=pagination_data,
            )

        # if no pagination
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data, status=200)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [BaseRBACPermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["company", "department", "designation"]
    search_fields = ["name", "email", "mobile", "designation"]
    ordering_fields = ["name", "hired_on"]
    ordering = ["id"]
    pagination_class = CustomPagination

    @action(detail=False, methods=["get"])
    def me(self, request):
        emp = Employee.objects.filter(user=request.user).first()
        if not emp:
            return CustomResponse(data="No employee record found.", status=404)
        serializer = self.get_serializer(emp)
        return CustomResponse(serializer.data, status=200)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ["ADMIN", "MANAGER"]:
            raise PermissionDenied("Not allowed.")

        if user.role == "MANAGER":
            if serializer.validated_data.get("company") != user.company:
                raise PermissionDenied(
                    "Managers can only create employees in their company."
                )
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        validated_data = serializer.validated_data

        # Employee rules
        if user.role == "EMPLOYEE":
            if instance.user != user:
                raise PermissionDenied("Employees can only update their own record.")

            # Check if restricted fields are being *changed*
            restricted_fields = ["company", "department", "user"]
            for field in restricted_fields:
                if field in validated_data:
                    new_value = validated_data[field]
                    old_value = getattr(instance, field)
                    if new_value != old_value:
                        raise PermissionDenied(f"Employees cannot change {field}.")

        # Manager rules
        elif user.role == "MANAGER":
            if instance.company != user.company:
                raise PermissionDenied("Managers can only update employees in their company.")

            if "company" in validated_data and validated_data["company"] != instance.company:
                raise PermissionDenied("Managers cannot change an employee's company.")

            if "department" in validated_data and validated_data["department"] != instance.department:
                raise PermissionDenied("Managers cannot change an employee's department.")

            if "user" in validated_data:
                new_user = validated_data["user"]
                if new_user.company != user.company:
                    raise PermissionDenied(
                        "Managers can only assign users from their own company."
                    )

        # Admin → unrestricted

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        # If user is EMPLOYEE
        if user.role == "EMPLOYEE":
            # Block deleting themselves
            if instance.user == user:
                raise PermissionDenied("Employees cannot delete themselves.")

        if user.role == "MANAGER":
            if instance.company != user.company:
                raise PermissionDenied(
                    "Managers can only delete employees in their own company."
                )

        # If passes checks → delete
        instance.delete()

    def list(self, request, *args, **kwargs):
        user = request.user

        # Role-based filtering
        if user.role == "ADMIN":
            queryset = Employee.objects.all()
        elif user.role == "MANAGER" and user.company_id:
            queryset = Employee.objects.filter(company_id=user.company_id)
        elif user.role == "EMPLOYEE":
            queryset = Employee.objects.filter(user=user)
        else:
            queryset = Employee.objects.none()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination_data = self.paginator.get_pagination_meta()
            return CustomResponse(
                data=serializer.data,
                status=200,
                pagination=pagination_data,
            )

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data, status=200)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data, status=200)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return CustomResponse(data=response.data, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return CustomResponse(data=response.data, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return CustomResponse(data=response.data, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return CustomResponse(
            data={}, status=response.status_code, message="Deleted successfully"
        )


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [BaseRBACPermission]
    pagination_class = CustomPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "company",
        "department",
        "start_date",
        "end_date",
        "assigned_employees",
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_date", "end_date"]

    def list(self, request, *args, **kwargs):
        user = request.user
        # Role-based filtering
        if user.role == "ADMIN":
            queryset = Project.objects.all()
        elif user.role in ["MANAGER", "EMPLOYEE"]:
            queryset = Project.objects.filter(company_id=user.company_id)
        else:  # no company
            queryset = Project.objects.none()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination_data = self.paginator.get_pagination_meta()
            return CustomResponse(
                data=serializer.data,
                status=200,
                pagination=pagination_data,
            )

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data, status=200)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data, status=200)

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role not in ["ADMIN", "MANAGER"]:
            raise PermissionDenied("You do not have permission to create projects.")

        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return CustomResponse(data=serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if user.role == "EMPLOYEE":
            raise PermissionDenied("Employees cannot update projects.")

        if user.role == "MANAGER" and instance.company_id != user.company_id:
            raise PermissionDenied("You cannot update projects from another company.")

        serializer = self.get_serializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return CustomResponse(data=serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if user.role == "EMPLOYEE":
            raise PermissionDenied("Employees cannot delete projects.")

        if user.role == "MANAGER" and instance.company_id != user.company_id:
            raise PermissionDenied("You cannot delete projects from another company.")

        instance.delete()
        return CustomResponse(message="Project deleted successfully", status=204)
