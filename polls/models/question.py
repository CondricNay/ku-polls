import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .choice import Choice
from .vote import Vote


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
