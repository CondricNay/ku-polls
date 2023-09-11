import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import now_plus, Question

# Create your tests here.
class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self) -> None:
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = now_plus(30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self) -> None:
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = now_plus(-1) - datetime.timedelta(seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self) -> None:
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = now_plus() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_future_pub_date(self) -> None:
        """
        Test that a question with a future pub date is not considered published.
        """
        future_pub_date = now_plus(1)
        question = Question(question_text="Future Question", pub_date=future_pub_date)
        self.assertFalse(question.is_published())

    def test_is_published_default_pub_date(self) -> None:
        """
        Test that a question with the default pub date (now) is considered published.
        """
        question = Question(question_text="Default Pub Date Question")
        self.assertTrue(question.is_published())

    def test_is_published_past_pub_date(self) -> None:
        """
        Test that a question with a past pub date is considered published.
        """
        past_pub_date = now_plus(-1)
        question = Question(question_text="Past Question", pub_date=past_pub_date)
        self.assertTrue(question.is_published())

    def test_can_vote_within_date_range(self) -> None:
        """
        Test that a user can vote when the pub date is in the past and the end date is in the future.
        """
        past_pub_date = now_plus(-1)
        future_end_date = now_plus(1)
        question = Question(question_text="Votable Question", pub_date=past_pub_date, end_date=future_end_date)
        self.assertTrue(question.can_vote())

    def test_cannot_vote_before_pub_date(self) -> None:
        """
        Test that a user cannot vote before the pub date.
        """
        future_pub_date = now_plus(1)
        future_end_date = now_plus(2)
        question = Question(question_text="Not Yet Votable Question", pub_date=future_pub_date, end_date=future_end_date)
        self.assertFalse(question.can_vote())

    def test_cannot_vote_after_end_date(self):
        """
        Test that a user cannot vote after the end date.
        """
        past_pub_date = now_plus(-2)
        past_end_date = now_plus(-1)
        question = Question(question_text="Expired Question", pub_date=past_pub_date, end_date=past_end_date)
        self.assertFalse(question.can_vote())


def create_question(question_text, days) -> Question:
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self) -> None:
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self) -> None:
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self) -> None:
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self) -> None:
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self) -> None:
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self) -> None:
        """
        The detail view of a question with a pub_date in the future
        redirects to index view.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse('polls:index'))

    def test_past_question(self) -> None:
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)