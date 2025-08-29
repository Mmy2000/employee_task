🚀 Features

Authentication & RBAC

JWT Authentication (Login/Refresh)

Roles: ADMIN, MANAGER, EMPLOYEE

Fine-grained access:

Admin → full control

Manager → restricted to own company

Employee → only own profile & reviews

Company & Department Management

View companies with auto-calculated counts

View departments by company

Employee Management

CRUD operations (role-based restrictions)

Auto-calculated days employed

/api/employees/me/ endpoint for employees

Project Management (Bonus)

CRUD with assigned employees

Linked to company & department

Performance Review Workflow

Pending → Scheduled → Feedback Provided → Under Approval → Approved/Rejected → Rework

Workflow actions secured (only Admin/Manager can process, employee can only view)

Custom API Responses

Unified JSON structure with status, message, data, pagination

Custom Pagination

Page info: current, total, per_page, first/last page

API Documentation

OpenAPI schema (/api/schema/)

Swagger UI (/api/docs/)

Testing

Unit tests for models and workflow transitions

Integration tests for endpoints and permissions
