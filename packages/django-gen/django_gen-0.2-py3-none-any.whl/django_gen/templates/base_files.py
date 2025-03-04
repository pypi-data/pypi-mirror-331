BASE_MODEL = """from django.db import models
from django.contrib.auth.models import User


class CustomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class BaseModel(models.Model):
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='%(app_label)s_%(class)s_created_by', )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   blank=True, null=True, related_name='%(app_label)s_%(class)s_updated_by')

    objects = CustomManager()

    class Meta:
        abstract = True
"""

BASE_SERIALIZER = """from rest_framework import serializers

class BaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, "added_at"):
            data["added_at"] = instance.added_at.strftime("%Y-%m-%d %H:%M")
        if hasattr(instance, "updated_at"):
            data["updated_at"] = instance.updated_at.strftime("%Y-%m-%d %H:%M")
        return data


def build_relational_model_serializer(model_, fields_=None, exclude_=None, ref_name_=None):
    class RelationalSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_
            if fields_ is not None:
                fields = fields_
            else:
                exclude = exclude_
            ref_name = ref_name_

    return RelationalSerializer()

"""

BASE_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>
        {% block title %}
            
        {% endblock title %} | SiteName    
    </title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  </head>
  <body>
    {% block content %}
    
    {% endblock content %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  </body>
</html>
"""
