---
description: How to add a new Django API Endpoint
---
# Add New API Endpoint Workflow

This workflow guides you through creating a new API endpoint in the Django backend and ensuring it is accessible to the Next.js frontend.

## Step 1: Define the Data Model (Optional)

If the endpoint requires a new database table, define it in `backend/portfolio/models.py`.

*Example:*
```python
class MyNewModel(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

**If you added a model, you MUST generate and run migrations:**
```bash
// turbo
cd backend && python manage.py makemigrations portfolio
// turbo
cd backend && python manage.py migrate
```

## Step 2: Create a Serializer

If returning complex data (like model instances), create a serializer in `backend/portfolio/serializers.py` to convert the data to JSON format.

*Example:*
```python
from rest_framework import serializers
from .models import MyNewModel

class MyNewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyNewModel
        fields = '__all__'
```

## Step 3: Create the View

Add a class-based view (using Django REST Framework) in `backend/portfolio/views.py`.

*Example:*
```python
from rest_framework import generics
from .models import MyNewModel
from .serializers import MyNewModelSerializer

class MyNewModelListView(generics.ListAPIView):
    queryset = MyNewModel.objects.all()
    serializer_class = MyNewModelSerializer
```

## Step 4: Register the URL Route

Expose the view over HTTP by adding a path in `backend/portfolio/urls.py`.

*Example:*
```python
from django.urls import path
from .views import MyNewModelListView

urlpatterns = [
    # ... existing routes ...
    path("new-feature/", MyNewModelListView.as_view(), name="new-feature-list"),
]
```

## Step 5: Verify the Endpoint

Test that the endpoint works locally.

```bash
curl http://localhost:8000/api/new-feature/
```
