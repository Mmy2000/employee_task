# core/serializers.py
from rest_framework import serializers
from django.db.models import Count
from .models import Company, Department, Employee, Project
from rest_framework.exceptions import PermissionDenied


class CompanySerializer(serializers.ModelSerializer):
    departments_count = serializers.IntegerField(read_only=True)
    employees_count = serializers.IntegerField(read_only=True)
    projects_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "departments_count",
            "employees_count",
            "projects_count",
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    employees_count = serializers.IntegerField(read_only=True)
    projects_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ["id", "company", "name", "employees_count", "projects_count"]


class EmployeeSerializer(serializers.ModelSerializer):
    days_employed = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "company",
            "department",
            "user",
            "name",
            "email",
            "mobile",
            "address",
            "designation",
            "hired_on",
            "days_employed",
        ]
        extra_kwargs = {
            "company": {"required": False},
            "department": {"required": False},
        }

    def validate(self, attrs):
        company = attrs.get("company") or getattr(self.instance, "company", None)
        department = attrs.get("department") or getattr(
            self.instance, "department", None
        )
        print(company,department)

        if company and department:
            if department.company != company:
                raise serializers.ValidationError(
                    {"department": "Department must belong to the selected company."}
                )

        return attrs

    def get_days_employed(self, obj):
        return obj.days_employed


class ProjectSerializer(serializers.ModelSerializer):
    assigned_employees = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all()
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "company",
            "department",
            "name",
            "description",
            "start_date",
            "end_date",
            "assigned_employees",
        ]

    def validate(self, data):
        """Custom validation for role restrictions"""
        user = self.context["request"].user

        # --- Employees cannot create or update projects at all ---
        if user.role == "EMPLOYEE":
            raise PermissionDenied("Employees cannot create or update projects.")

        # --- Manager / Admin restrictions ---
        if user.role == "MANAGER":
            # Check company restriction
            if "company" in data:
                if data["company"].id != user.company_id:
                    raise PermissionDenied(
                        "You cannot create/update projects for other companies."
                    )

            # Check department restriction
            if "department" in data:
                if data["department"].company_id != user.company_id:
                    raise PermissionDenied(
                        "You cannot assign a department from another company."
                    )

            # Check assigned employees restriction
            if "assigned_employees" in data:
                for emp in data["assigned_employees"]:
                    if emp.company_id != user.company_id:
                        raise PermissionDenied(
                            f"Employee {emp.id} does not belong to your company."
                        )
        if user.role == "ADMIN":
            # Check department restriction
            if "department" in data:
                if data["department"].company_id != user.company_id:
                    raise PermissionDenied(
                        "You cannot assign a department from another company."
                    )

            # Check assigned employees restriction
            if "assigned_employees" in data:
                for emp in data["assigned_employees"]:
                    if emp.company_id != user.company_id:
                        raise PermissionDenied(
                            f"Employee {emp.id} does not belong to your company."
                        )

        return data
