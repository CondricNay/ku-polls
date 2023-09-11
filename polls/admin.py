from django.contrib import admin

from .models import Choice, Question

# Register your models here.
model_list = [
    Choice,
    Question
]

admin.site.register(model_list)
