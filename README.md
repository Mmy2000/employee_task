# 🌐 Company Management System – Backend  

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)  
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)  
![DRF](https://img.shields.io/badge/DRF-REST%20Framework-red?logo=django&logoColor=white)  
![License](https://img.shields.io/badge/License-MIT-yellow)  
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?logo=pytest)  

A **role-based backend system** built with **Django + Django REST Framework** for managing **companies, departments, employees, projects, and performance reviews**.  

---

## ✨ Features  

✅ **JWT Authentication & RBAC** (Admin, Manager, Employee)  
✅ **Companies & Departments** with counts  
✅ **Employees** CRUD with self-service (`/me/`) endpoint  
✅ **Projects** linked to companies & departments  
✅ **Performance Review Workflow** (schedule → feedback → approval)  
✅ **Custom API Response & Pagination** for consistency  
✅ **OpenAPI Docs** via Swagger & Redoc  
✅ **Unit & Integration Tests** with pytest  

---

## 🗂️ Project Structure  

│── accounts/ # Users, Auth, Permissions
│── core/ # Company, Department, Employee, Project
│── reviews/ # Performance Reviews Workflow
│── config/ # Settings, URLs, Custom Response & Pagination
│── tests/ # Unit & Integration Tests
│── manage.py


---

## 🛠️ Tech Stack  

- ⚡ **Python 3.11+**  
- 🟢 **Django 5**  
- 🔴 **Django REST Framework (DRF)**  
- 🔐 **JWT Authentication (djangorestframework-simplejwt)**  
- 🐘 **PostgreSQL** (SQLite supported for local dev)  
- 🧪 **pytest + pytest-django**  

---

## 🔑 Authentication  

All secured endpoints require a JWT token:  

```http
Authorization: Bearer <your-access-token>

⚙️ Installation
1️⃣ Clone the repo
git clone https://github.com/Mmy2000/employee_task.git
cd employee_task

2️⃣ Setup environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure .env
5️⃣ Run migrations & create superuser
python manage.py migrate
python manage.py createsuperuser

6️⃣ Start the server
python manage.py runserver

📖 API Docs
Swagger UI → http://localhost:8000/api/docs/
Redoc → http://localhost:8000/api/redoc/
OpenAPI JSON → http://localhost:8000/api/schema/
