from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Question, Choice, Vote, AuthorizedUser, now_plus


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        future_time = now_plus(30)  # Add 30 days to the current time
        future_question = Question(pub_date=future_time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        old_time = now_plus(-2)  # Subtract 2 days from the current time
        old_question = Question(pub_date=old_time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        recent_time = now_plus(-0.5)  # Subtract 0.5 days from the current time (12 hours)
        recent_question = Question(pub_date=recent_time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_future_pub_date(self):
        """
        Test that a question with a future pub date isn't considered published.
        """
        future_time = now_plus(1)  # Add 1 day to the current time
        future_question = Question(pub_date=future_time)
        self.assertFalse(future_question.is_published())

    def test_is_published_default_pub_date(self):
        """
        Test that a question with the default pub date (now) is considered published.
        """
        default_pub_question = Question(question_text="Default Pub Date Question")
        self.assertTrue(default_pub_question.is_published())

    def test_is_published_past_pub_date(self):
        """
        Test that a question with a past pub date is considered published.
        """
        past_time = now_plus(-1)  # Subtract 1 day from the current time
        past_question = Question(pub_date=past_time)
        self.assertTrue(past_question.is_published())


class ChoiceModelTests(TestCase):
    def test_get_percentage_vote(self):
        """
        Test that the percentage of votes for a choice is calculated correctly.
        """
        question = Question.objects.create(
            question_text="Sample Question",
            pub_date=now_plus(-1),  # Subtract 1 day from the current time
            end_date=now_plus(1)    # Add 1 day to the current time
        )
        choice1 = Choice.objects.create(
            question=question,
            choice_text="Choice 1"
        )
        choice2 = Choice.objects.create(
            question=question,
            choice_text="Choice 2"
        )
        user = User.objects.create_user(username='testuser', password='testpass')
        Vote.objects.create(user=user, choice=choice1)
        Vote.objects.create(user=user, choice=choice2)

        self.assertEqual(choice1.get_percentage_vote(), 50.0)
        self.assertEqual(choice2.get_percentage_vote(), 50.0)


class AuthorizedUserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(
            question_text="Sample Question",
            pub_date=now_plus(-1),  # Subtract 1 day from the current time
            end_date=now_plus(1)    # Add 1 day to the current time
        )
        self.authorized_user = AuthorizedUser(user=self.user)

    def test_can_vote_authenticated(self):
        """
        Test that an authenticated user can vote when the question is published.
        """
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('polls:detail', args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.authorized_user.can_vote(response.wsgi_request, self.question))

    def test_cannot_vote_unauthenticated(self):
        """
        Test that an unauthenticated user cannot vote.
        """
        response = self.client.get(reverse('polls:detail', args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.authorized_user.can_vote(response.wsgi_request, self.question))

    def test_get_existing_vote(self):
        """
        Test that the existing vote for a user and question is retrieved correctly.
        """
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('polls:detail', args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)

        choice = Choice.objects.create(
            question=self.question,
            choice_text="Choice 1"
        )
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': choice.id})
        self.assertEqual(response.status_code, 302)  # Redirect to results page

        existing_vote = self.authorized_user.get_existing_vote(response.wsgi_request, self.question)
        self.assertIsNotNone(existing_vote)


class ViewsTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        question = Question.objects.create(
            question_text="Past question.",
            pub_date=now_plus(-1)  # Subtract 1 day from the current time
        )
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_index_view_with_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        """
        Question.objects.create(
            question_text="Future question.",
            pub_date=now_plus(1)  # Add 1 day to the current time
        )
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_detail_view_with_future_question(self):
        """
        The detail view of a question with a pub_date in the future redirects to index view.
        """
        future_question = Question.objects.create(
            question_text='Future question.',
            pub_date=now_plus(1)  # Add 1 day to the current time
        )
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse('polls:index'))

    def test_detail_view_with_past_question(self):
        """
        The detail view of a question with a pub_date in the past displays the question's text.
        """
        past_question = Question.objects.create(
            question_text='Past Question.',
            pub_date=now_plus(-1)  # Subtract 1 day from the current time
        )
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_vote_view_authenticated_user(self):
        """
        Test that an authenticated user can vote and is redirected to the results view.
        """
        user = User.objects.create_user(username='testuser', password='testpass')
        question = Question.objects.create(
            question_text="Sample Question",
            pub_date=now_plus(-1),  # Subtract 1 day from the current time
            end_date=now_plus(1)    # Add 1 day to the current time
        )
        choice = Choice.objects.create(
            question=question,
            choice_text="Choice 1"
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('polls:vote', args=(question.id,)), {'choice': choice.id})
        self.assertRedirects(response, reverse('polls:results', args=(question.id,)))

    def test_vote_view_unauthenticated_user(self):
        """
        Test that an unauthenticated user cannot vote and is redirected to the login page.
        """
        question = Question.objects.create(
            question_text="Sample Question",
            pub_date=now_plus(-1),  # Subtract 1 day from the current time
            end_date=now_plus(1)    # Add 1 day to the current time
        )
        choice = Choice.objects.create(
            question=question,
            choice_text="Choice 1"
        )
        response = self.client.post(reverse('polls:vote', args=(question.id,)), {'choice': choice.id})

        # Check if the response is a redirect to the login page with a 'next' parameter
        self.assertEqual(response.status_code, 302)  # 302 is a redirect status
        self.assertRedirects(response, reverse('login') + f'?next={reverse("polls:vote", args=(question.id,))}')

    def test_vote_view_with_valid_choice(self):
        """
        Test that the vote view handles a valid choice correctly.
        """
        user = User.objects.create_user(username='testuser', password='testpass')
        question = Question.objects.create(
            question_text="Sample Question",
            pub_date=now_plus(-1),  # Subtract 1 day from the current time
            end_date=now_plus(1)    # Add 1 day to the current time
        )
        choice = Choice.objects.create(
            question=question,
            choice_text="Choice 1"
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('polls:vote', args=(question.id,)), {'choice': choice.id})
        self.assertRedirects(response, reverse('polls:results', args=(question.id,)))

    def test_vote_view_with_invalid_choice(self):
        """
        Test that the vote view handles an invalid choice gracefully.
        """
        user = User.objects.create_user(username='testuser', password='testpass')
        question = Question.objects.create(
            question_text="Sample Question",
            pub_date=now_plus(-1),  # Subtract 1 day from the current time
            end_date=now_plus(1)    # Add 1 day to the current time
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('polls:vote', args=(question.id,)), {'choice': 42})
        self.assertRedirects(response, reverse('polls:detail', args=(question.id,)))
