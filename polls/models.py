import datetime

from django.db import models
from django.db.models import Max, Min, Sum
from django.utils import timezone


def now_plus(added_day: int = 0) -> datetime:
    return timezone.now() + timezone.timedelta(days=added_day)


class Question(models.Model):
    """
    Model representing a poll question.
    """
    def pub_date_default() -> datetime:
        return now_plus(0)

    def end_date_default() -> datetime:
        return now_plus(1)

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=pub_date_default,
                                    verbose_name='published date')
    end_date = models.DateTimeField(default=end_date_default,
                                    verbose_name='end date')

    def was_published_recently(self) -> bool:
        """
        Check if the question was published within the last 24 hours.
        """
        return now_plus(-1) <= self.pub_date <= now_plus(0)

    def is_published(self) -> bool:
        return self.pub_date <= now_plus(0)

    def can_vote(self) -> bool:
        # todo add more conditions in iteration3 and move this to User class
        if self.pub_date <= now_plus(0) <= self.end_date:
            return True
        else:
            return False

    def get_remaining_time(self) -> datetime:
        """
        Return the time remaining (time difference) until a poll end.
        If a poll has ended, it will return zero time difference.

        Then format it without microseconds.
        """
        remaining_time = max(self.end_date - now_plus(0),
                             timezone.timedelta(0))

        return str(remaining_time).split(".")[0]

    def get_all_votes(self) -> int:
        all_choices = Choice.objects.filter(question=self.id)
        all_votes = all_choices.aggregate(all_votes=Sum('votes'))['all_votes']
        return all_votes

    def get_max_vote(self):
        all_choices = Choice.objects.filter(question=self.id)
        max_vote = all_choices.aggregate(max_vote=Max('votes'))['max_vote']
        return max_vote

    def get_min_vote(self):
        all_choices = Choice.objects.filter(question=self.id)
        min_vote = all_choices.aggregate(min_vote=Min('votes'))['min_vote']
        return min_vote

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

    def get_each_vote(self) -> int:
        current_choice = Choice.objects.get(id=self.id)
        return current_choice.votes

    def get_percentage_vote(self) -> float:
        return (self.get_each_vote()/self.question.get_all_votes())*100

    def __str__(self) -> str:
        """
        Return a string representation of the choice.
        """
        return self.choice_text
