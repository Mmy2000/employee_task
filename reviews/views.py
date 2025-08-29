# reviews/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import EmployeeReview
from .serializers import EmployeeReviewSerializer
from config.response import CustomResponse
from rest_framework.exceptions import PermissionDenied

class EmployeeReviewViewSet(viewsets.ModelViewSet):
    queryset = EmployeeReview.objects.select_related("employee")
    serializer_class = EmployeeReviewSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "ADMIN":
            return qs
        if user.role == "MANAGER" and user.company_id:
            return qs.filter(employee__company_id=user.company_id)
        if user.role == "EMPLOYEE" and user.company_id:
            return qs.filter(
                employee__company_id=user.company_id, user=user
            )
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "ADMIN":
            serializer.save()
        elif user.role == "MANAGER":
            # Managers can only create for employees in their company
            emp = serializer.validated_data["employee"]
            if emp.company_id != user.company_id:
                raise PermissionDenied("Managers can only create reviews for employees in their own company.")
            serializer.save()
        else:
            raise PermissionDenied("Employees cannot create reviews.")

    def _check_admin_or_manager(self, review):
        user = self.request.user
        if user.role == "ADMIN":
            return
        if user.role == "MANAGER" and review.employee.company_id == user.company_id:
            return
        raise PermissionDenied(
            "Only admin or manager of the same company can perform this action."
        )

    @action(detail=True, methods=["post"])
    def schedule(self, request, pk=None):
        review = self.get_object()
        self._check_admin_or_manager(review)  # guard
        review.schedule(request.data.get("review_date"), request.user)
        review.save()
        return CustomResponse(data=EmployeeReviewSerializer(review).data ,status=201)

    @action(detail=True, methods=["post"])
    def provide_feedback(self, request, pk=None):
        review = self.get_object()
        self._check_admin_or_manager(review)
        review.provide_feedback(request.data.get("feedback", ""), request.user)
        review.save()
        return CustomResponse(data=EmployeeReviewSerializer(review).data, status=201)

    @action(detail=True, methods=["post"])
    def submit_for_approval(self, request, pk=None):
        review = self.get_object()
        self._check_admin_or_manager(review)
        review.submit_for_approval()
        review.save()
        return CustomResponse(data=EmployeeReviewSerializer(review).data, status=201)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        review = self.get_object()
        self._check_admin_or_manager(review)
        review.approve(request.user)
        review.save()
        return CustomResponse(data=EmployeeReviewSerializer(review).data, status=201)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        review = self.get_object()
        self._check_admin_or_manager(review)
        review.reject(request.user)
        review.save()
        return CustomResponse(data=EmployeeReviewSerializer(review).data, status=201)

    @action(detail=True, methods=["post"])
    def rework_feedback(self, request, pk=None):
        review = self.get_object()
        self._check_admin_or_manager(review)
        review.rework_feedback(request.data.get("feedback", ""), request.user)
        review.save()
        return CustomResponse(data=EmployeeReviewSerializer(review).data, status=201)
