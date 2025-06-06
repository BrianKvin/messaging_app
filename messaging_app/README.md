# 📬 Messaging API with Django REST Framework

This project guides learners through designing and implementing a **robust messaging API** using Django and Django REST Framework (DRF). It covers every step from project setup to API endpoint creation, with an emphasis on **modularity**, **relationships**, and **best practices**.

---

## 🚀 Overview

This API allows users to:

- Create conversations between multiple users.
- Send messages within conversations.
- Retrieve messages and conversation details.

The system uses Django's ORM for relational modeling and DRF for building RESTful endpoints.

---

## 🎯 Project Objectives

By completing this project, you will:

- Scaffold a Django project and app.
- Define scalable data models using Django's ORM.
- Handle one-to-many and many-to-many relationships.
- Implement serializers and nested data structures in DRF.
- Create and test API endpoints using viewsets and routers.
- Structure your project using Django best practices.

---

## 📂 Project Structure

- `chats/` – The messaging app (models, views, serializers, urls).
- `messaging_app/` – Project configuration and global routing.
- `manage.py` – Django CLI entry point.
- `requirements.txt` – Dependency list.
- `README.md` – This documentation.

---

## 📐 Key Implementation Phases

### 0. ✅ Project Setup

```bash
django-admin startproject messaging_app
cd messaging_app
python manage.py startapp chats
pip install djangorestframework
