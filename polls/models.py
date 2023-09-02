import datetime

from django.db import models
from django.utils import timezone

# Create your models here.

class Question(models.Model):
    """
    Model representing a poll question.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self) -> bool:
        """
        Check if the question was published within the last 24 hours.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self) -> str:
        """
        Return a string representation of the question.
        """
        return self.question_text


class Choice(models.Model):
    """
    Model representing choices for a poll question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        """
        Return a string representation of the choice.
        """
        return self.choice_text

