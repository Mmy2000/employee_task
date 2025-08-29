# accounts/tests/test_permissions.py
import pytest
from rest_framework.test import APIClient
from core.models import Company, Department, Employee
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_employee_can_only_see_self():
    company = Company.objects.create(name="TestCorp")
    dept = Department.objects.create(company=company, name="IT")
    emp1 = Employee.objects.create(
        company=company, department=dept, name="Sara", email="sara@corp.com"
    )
    emp2 = Employee.objects.create(
        company=company, department=dept, name="Ali", email="ali@corp.com"
    )

    user = User.objects.create_user(
        email="sara@corp.com",
        password="pass",
        role="EMPLOYEE",
        company=company,
        username="test",
    )

    # link user to employee
    emp1.user = user
    emp1.save()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/core/api/employees/")
    assert response.status_code == 200
    assert len(response.data["data"]) == 1
    assert response.data["data"][0]["email"] == "sara@corp.com"
