import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest
from django.utils import timezone


def now_plus(added_day: int = 0) -> datetime:
    """
    Return the current time with an optional offset in days.
    """
    return timezone.now() + timezone.timedelta(days=added_day)


class Question(models.Model):
    """
    Model representing a poll question.
    """
    def pub_date_default() -> datetime:
        """
        Default value for the 'pub_date' field.
        """
        return now_plus(0)

    def end_date_default() -> datetime:
        """
        Default value for the 'end_date' field.

        Returns:
            datetime: The current time plus one day.
        """
        return now_plus(1)

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=pub_date_default,
                                    verbose_name='published date')
    end_date = models.DateTimeField(default=end_date_default,
                                    verbose_name='end date')

    def clean(self) -> None:
        """
        Custom validation to ensure pub_date is earlier than end_date.
        """
        if self.pub_date >= self.end_date:
            raise ValidationError("The 'published date' must be earlier than the 'end date'.")

    def save(self, *args, **kwargs) -> None:
        """
        Override the save method to ensure clean() is called before saving.
        """
        self.clean()
        super().save(*args, **kwargs)

    def was_published_recently(self) -> bool:
        """
        Check if the question was published within the last 24 hours.

        Returns:
            bool: True if the question was published recently, False otherwise.
        """
        return now_plus(-1) <= self.pub_date <= now_plus(0)

    def is_published(self) -> bool:
        """
        Check if the question is currently published.

        Returns:
            bool: True if the question is published, False otherwise.
        """
        return self.pub_date <= now_plus(0) <= self.end_date

    def get_remaining_time(self) -> str:
        """
        Return the time remaining (time difference) until a poll ends.
        If a poll has ended, it will return zero time difference.

        Returns:
            str: The remaining time as formatted string without microseconds.
        """
        remaining_time = max(self.end_date - now_plus(0), timezone.timedelta(0))
        return str(remaining_time).split(".")[0]

    def get_all_votes(self) -> int:
        """
        Get the total number of votes for this question.

        Returns:
            int: The total number of votes.
        """
        related_choices = Choice.objects.filter(question=self)
        all_votes = Vote.objects.filter(choice__in=related_choices).count()
        return all_votes

    def __str__(self) -> str:
        """
        Return a string representation of the question.

        Returns:
            str: The question text.
        """
        return self.question_text


class Choice(models.Model):
    """
    Model representing choices for a poll question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self) -> int:
        """
        Get the number of votes for this choice.

        Returns:
            int: The number of votes.
        """
        return self.vote_set.count()

    def get_percentage_vote(self) -> float:
        """
        Calculate the percentage of votes for this choice among all votes for the question.

        Returns:
            float: The percentage of votes for this choice.
        """
        return (self.votes / self.question.get_all_votes()) * 100

    def __str__(self) -> str:
        """
        Return a string representation of the choice.

        Returns:
            str: The choice text.
        """
        return self.choice_text


class AuthorizedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def can_vote(self, request: HttpRequest, question: Question) -> bool:
        """
        Check if the user can vote on a given question.

        Args:
            request (HttpRequest): The HTTP request object.
            question (Question): The question to check for voting eligibility.

        Returns:
            bool: True if the user can vote, False otherwise.
        """
        return question.is_published() and request.user.is_authenticated

    def get_existing_vote(self, request: HttpRequest, question: Question) -> 'Vote':
        """
        Get the existing vote of the user for a given question.

        Args:
            request (HttpRequest): The HTTP request object.
            question (Question): The question to retrieve the vote for.

        Returns:
            Vote: The existing vote of the user for the question, or None if no vote exists.
        """
        existing_vote = Vote.objects.filter(user=request.user,
                                        choice__question=question).first()
        return existing_vote

    def submit_vote(self, request: HttpRequest, question: Question) -> None:
        """
        Submit a vote for the user on a given question.

        Args:
            request (HttpRequest): The HTTP request object.
            question (Question): The question to vote on.
        """
        if self.can_vote(request, question):
            new_choice = Choice.objects.get(pk=request.POST["choice"])
            existing_vote = self.get_existing_vote(request, question)

            if existing_vote is None:
                new_vote = Vote(user=request.user, choice=new_choice)
                new_vote.save()
            else:
                existing_vote.choice = new_choice
                existing_vote.save()

            self.update_session(request, question)

    def update_session(self, request: HttpRequest, question: Question) -> None:
        """
        Update the session with the user's recent question and choice.

        Args:
            request (HttpRequest): The HTTP request object.
            question (Question): The question that the user voted on.
        """
        recent_question_ids = request.session.get('recent_question_ids', [])
        recent_choice_ids = request.session.get('recent_choice_ids', [])

        try:
            index = recent_question_ids.index(question.id)
            recent_choice_ids[index] = int(request.POST["choice"])
        except ValueError:
            recent_question_ids.append(int(question.id))
            recent_choice_ids.append(int(request.POST["choice"]))

        request.session['recent_question_ids'] = recent_question_ids
        request.session['recent_choice_ids'] = recent_choice_ids


class Vote(models.Model):
    """
    Records a Vote.
    """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
