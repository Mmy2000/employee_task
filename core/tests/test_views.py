import pytest
from rest_framework.test import APIClient
from core.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_company_list_admin_can_see_all():
    company1 = Company.objects.create(name="TestCorp1")
    company2 = Company.objects.create(name="TestCorp2")
    admin = User.objects.create_user(
        email="admin@test.com", password="pass", role="ADMIN",username="test"
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get("/core/api/companies/")
    assert response.status_code == 200
    assert len(response.data["data"]) == 2  # using your CustomResponse
