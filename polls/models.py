import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max, Min
from django.http import HttpRequest
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
        return self.pub_date <= now_plus(0) <= self.end_date

    def get_remaining_time(self) -> str:
        """
        Return the time remaining (time difference) until a poll end.
        If a poll has ended, it will return zero time difference.

        Then format it without microseconds.
        """
        remaining_time = max(self.end_date - now_plus(0),
                             timezone.timedelta(0))

        return str(remaining_time).split(".")[0]

    def get_all_votes(self) -> int:
        # bug here, something like Vote.object.filter(choice_set=self).count()????
        all_choices = Choice.objects.filter(question=self.id)
        return all_choices.count()

    def get_max_vote(self) -> int:
        all_choices = Choice.objects.filter(question=self.id)
        max_vote = all_choices.aggregate(max_vote=Max('votes'))['max_vote']
        return max_vote

    def get_min_vote(self) -> int:
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

    @property
    def votes(self):
        return self.vote_set.count()

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


class AuthorizedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def can_vote(self, request: HttpRequest, question: Question) -> bool:
        return question.is_published() and request.user.is_authenticated

    def get_existing_vote(self, request: HttpRequest, question: Question) -> 'Vote':
        existing_vote = Vote.objects.filter(user=request.user, choice__question=question).first()
        return existing_vote

    def submit_vote(self, request: HttpRequest, question: Question) -> None:
        if self.can_vote(request, question):
            new_choice = Choice.objects.get(pk=request.POST["choice"])
            existing_vote =  self.get_existing_vote(request, question)

            if existing_vote is None:
                new_vote = Vote(user=request.user, choice=new_choice)
                new_vote.save()
            else:
                existing_vote.choice = new_choice
                existing_vote.save()

            self.update_session(request, question)

    def update_session(self, request: HttpRequest, question: Question) -> None:
        # Get the existing 'recent_question_ids' list from the session or create an empty list if it doesn't exist
        recent_question_ids = request.session.get('recent_question_ids', [])

        # Get the existing 'recent_choice_ids' list from the session or create an empty list if it doesn't exist
        recent_choice_ids = request.session.get('recent_choice_ids', [])
        
        for i in range(len(recent_question_ids)):
            if recent_question_ids[i] == question.id:
                recent_choice_ids[i] = int(request.POST["choice"])
                break

        else:
            # Append the new values to the lists
            recent_question_ids.append(int(question.id))
            recent_choice_ids.append(int(request.POST["choice"]))

        # Update the session variables with the new lists
        request.session['recent_question_ids'] = recent_question_ids
        request.session['recent_choice_ids'] = recent_choice_ids


class Vote(models.Model):
    """Records a Vote """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)