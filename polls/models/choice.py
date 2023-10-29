from django.core.exceptions import ValidationError
from django.db import models


class Choice(models.Model):
    """
    Model representing choices for a poll question.
    """
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self) -> int:
        """
        Get the number of votes for this choice.

        Returns:
            int: The number of votes.
        """
        return self.vote_set.count()

    def clean(self) -> None:
        """
        Custom validation to ensure that the choice_text is unique among existing choices.
        Raises a ValidationError if the choice_text is not unique.
        """
        text_exists = Choice.objects.filter(question=self.question,
                                            choice_text__iexact=self.choice_text).exists()

        if text_exists:
            raise ValidationError("Choice with this text already exists.")

    def save(self, *args, **kwargs) -> None:
        """
        Override the save method to ensure clean() is called before saving.
        """
        self.clean()
        super().save(*args, **kwargs)

    def get_percentage_vote(self) -> float:
        """
        Calculate the percentage of votes for this choice among all votes for the question.

        Returns:
            float: The percentage of votes for this choice.
        """
        all_votes = self.question.get_all_votes()
        if all_votes == 0:
            return 0
        
        return (self.votes / all_votes) * 100

    def __str__(self) -> str:
        """
        Return a string representation of the choice.

        Returns:
            str: The choice text.
        """
        return self.choice_text
