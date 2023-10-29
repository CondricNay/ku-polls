from django.contrib.auth.models import User
from django.db import models
from django.http import HttpRequest

from .choice import Choice
from .question import Question
from .vote import Vote


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
