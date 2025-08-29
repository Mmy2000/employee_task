# reviews/models.py
from django.db import models
from core.models import Employee
from django.conf import settings


class EmployeeReview(models.Model):
    class Stage(models.TextChoices):
        PENDING_REVIEW = "PENDING_REVIEW", "Pending Review"
        REVIEW_SCHEDULED = "REVIEW_SCHEDULED", "Review Scheduled"
        FEEDBACK_PROVIDED = "FEEDBACK_PROVIDED", "Feedback Provided"
        UNDER_APPROVAL = "UNDER_APPROVAL", "Under Approval"
        REVIEW_APPROVED = "REVIEW_APPROVED", "Review Approved"
        REVIEW_REJECTED = "REVIEW_REJECTED", "Review Rejected"

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="reviews"
    )
    current_stage = models.CharField(
        max_length=40, choices=Stage.choices, default=Stage.PENDING_REVIEW
    )

    # Optional fields for cycle metadata
    review_date = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_reviews",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Simple state machine guard methods
    def schedule(self, date, by_user):
        if self.current_stage != self.Stage.PENDING_REVIEW:
            raise ValueError("Can schedule only from Pending Review.")
        self.review_date = date
        self.submitted_by = by_user
        self.current_stage = self.Stage.REVIEW_SCHEDULED

    def provide_feedback(self, text, by_user):
        if self.current_stage != self.Stage.REVIEW_SCHEDULED:
            raise ValueError("Can provide feedback only after scheduling.")
        self.feedback = text
        self.submitted_by = by_user
        self.current_stage = self.Stage.FEEDBACK_PROVIDED

    def submit_for_approval(self):
        if self.current_stage != self.Stage.FEEDBACK_PROVIDED:
            raise ValueError("Submit for approval only after feedback.")
        self.current_stage = self.Stage.UNDER_APPROVAL

    def approve(self, manager_user):
        if self.current_stage != self.Stage.UNDER_APPROVAL:
            raise ValueError("Can approve only when under approval.")
        self.approved_by = manager_user
        self.current_stage = self.Stage.REVIEW_APPROVED

    def reject(self, manager_user):
        if self.current_stage != self.Stage.UNDER_APPROVAL:
            raise ValueError("Can reject only when under approval.")
        self.approved_by = manager_user
        self.current_stage = self.Stage.REVIEW_REJECTED

    def rework_feedback(self, text, by_user):
        if self.current_stage != self.Stage.REVIEW_REJECTED:
            raise ValueError("Rework only after rejection.")
        self.feedback = text
        self.submitted_by = by_user
        self.current_stage = self.Stage.FEEDBACK_PROVIDED
