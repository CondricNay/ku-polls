from django.contrib import admin

from .models import AuthorizedUser, Choice, Question, Vote

# Register your models here.
model_list = [
    AuthorizedUser,
    Choice,
    Question,
    Vote
]

admin.site.register(model_list)
