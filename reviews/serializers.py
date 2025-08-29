# reviews/serializers.py
from rest_framework import serializers
from .models import EmployeeReview


class EmployeeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeReview
        fields = [
            "id",
            "employee",
            "current_stage",
            "review_date",
            "feedback",
            "submitted_by",
            "approved_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["submitted_by", "approved_by", "created_at", "updated_at"]
