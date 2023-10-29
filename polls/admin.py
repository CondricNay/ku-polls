from django.contrib import admin

from .models.auth_user import AuthorizedUser
from .models.choice import Choice
from .models.question import Question
from .models.vote import Vote


# Register your models here.
model_list = [
    AuthorizedUser,
    Choice,
    Question,
    Vote
]

admin.site.register(model_list)
