import pytest
from reviews.models import EmployeeReview
from core.models import Employee, Company, Department
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


@pytest.mark.django_db
def test_employee_days_employed():
    company = Company.objects.create(name="TestCorp")
    dept = Department.objects.create(company=company, name="IT")
    emp = Employee.objects.create(
        company=company,
        department=dept,
        name="Sara",
        email="sara@corp.com",
        hired_on=date(2025, 1, 1),
        mobile="0100000000",
        address="Cairo",
        designation="Dev",
    )
    days = emp.days_employed
    assert days >= 0  # should return positive integer


@pytest.mark.django_db
def test_review_workflow_transitions():
    company = Company.objects.create(name="TestCorp")
    dept = Department.objects.create(company=company, name="IT")
    emp = Employee.objects.create(
        company=company,
        department=dept,
        name="Sara",
        email="sara@corp.com",
        designation="Dev",
    )
    admin = User.objects.create(email="admin@test.com", role="ADMIN")

    review = EmployeeReview.objects.create(employee=emp)
    assert review.current_stage == EmployeeReview.Stage.PENDING_REVIEW

    review.schedule("2025-09-10T10:00:00Z", admin)
    assert review.current_stage == EmployeeReview.Stage.REVIEW_SCHEDULED

    review.provide_feedback("Good job", admin)
    assert review.current_stage == EmployeeReview.Stage.FEEDBACK_PROVIDED

    review.submit_for_approval()
    assert review.current_stage == EmployeeReview.Stage.UNDER_APPROVAL

    review.approve(admin)
    assert review.current_stage == EmployeeReview.Stage.REVIEW_APPROVED
