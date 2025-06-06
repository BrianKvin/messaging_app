# messaging_app
 **Getting Started with Django REST Framework** resource:

````markdown
# 🚀 Getting Started with Django REST Framework (DRF)

This guide provides an overview of **Django REST Framework (DRF)**, its key architecture components, and how to set up a basic Django project integrated with DRF. By the end, you'll be able to:

- Understand the purpose and features of DRF.
- Familiarize yourself with its core components.
- Create and test a basic API endpoint.

---

## 🧠 Concept Overview

**Django REST Framework (DRF)** is a powerful and flexible toolkit for building Web APIs. It enhances Django's capabilities by making it easier to build RESTful APIs, providing features like:

- **Serialization**
- **Authentication & Permissions**
- **Browsable APIs**
- **ViewSets and Routers**

DRF abstracts much of the boilerplate involved in API development, so you can focus on your application logic.

---

## 📚 Topics Covered

1. Introduction to Django REST Framework
2. DRF Architecture: Serializers, ViewSets, Routers
3. Creating Your First API Endpoint

---

## 🎯 Learning Objectives

- Understand the purpose and features of Django REST Framework.
- Learn key components: **Serializers**, **ViewSets**, and **Routers**.
- Set up and run a basic DRF-powered API.

---

## 🔍 Introduction to Django REST Framework

DRF provides a structured, extensible way to create APIs with Django.

### ✅ Benefits of DRF

- **Serialization:** Converts Django models to JSON/XML formats.
- **ViewSets & Routers:** Streamlines API endpoint creation.
- **Authentication & Permissions:** Supports various auth schemes.
- **Browsable API:** Built-in web UI for testing and exploration.

---

## ⚙️ Creating Your First API Endpoint

Follow these steps to create a simple API for a `Book` model:

### 1. Create a Django Project and App

```bash
django-admin startproject my_project
cd my_project
python manage.py startapp my_app
````

### 2. Install Django REST Framework

```bash
pip install djangorestframework
```

Add `'rest_framework'` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
]
```

### 3. Define a Model (`models.py`)

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
```

### 4. Create a Serializer (`serializers.py`)

```python
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
```

### 5. Create a View (`views.py`)

```python
from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

### 6. Define a URL Route (`urls.py`)

```python
from django.urls import path
from .views import BookListCreateAPIView

urlpatterns = [
    path("api/books", BookListCreateAPIView.as_view(), name="book_list_create"),
]
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Access your API endpoint at:
📍 `http://localhost:8000/api/books`

---

## 🧪 Practice Exercises

* ➕ Extend `BookSerializer` to include a custom field showing the number of days since publication.
* 🔧 Install DRF in an existing Django project and create your own model-based API.
* 🧭 Use the browsable API interface to test various HTTP methods.
* 🧪 Experiment with additional serializer fields and view logic.

---

## 🔗 Additional Resources

* [📘 Django REST Framework Documentation](https://www.django-rest-framework.org/)
* [🚀 DRF Quickstart Tutorial](https://www.django-rest-framework.org/tutorial/quickstart/)
* [🔐 DRF Authentication Overview](https://www.django-rest-framework.org/api-guide/authentication/#authentication)
* [🔑 Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
* [🆔 Session Authentication](https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication)
* [🎥 Video: Django Authentication Explained (YouTube)](https://www.youtube.com/watch?v=_nZygPQ3gmo)

---

