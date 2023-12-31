from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest, \
                        HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import AuthorizedUser, Choice, Question


class IndexView(generic.ListView):
    """
    View for displaying a list of the latest poll questions.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self) -> QuerySet[Question]:
        """
        Return all the published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class DetailView(generic.DetailView):
    """
    View for displaying the details of a poll question.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self) -> QuerySet[Question]:
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs) -> HttpResponse | HttpResponseRedirect:
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.error(request, "You don't have access to that page")
            return redirect(reverse('polls:index'))


class ResultsView(generic.DetailView):
    """
    View for displaying the results of a poll question.
    """
    model = Question
    template_name = 'polls/results.html'


def sign_up(request) -> HttpResponse | HttpResponseRedirect:
    """
    View for user registration.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect(reverse('polls:index'))

        else:
            for each_error in form.errors.values():
                messages.error(request, each_error)

    else:
        form = UserCreationForm()

    return render(request, "registration/sign_up.html")


@login_required
def vote(request: HttpRequest, question_id: int) -> HttpResponseRedirect:
    """
    View for submitting votes on poll questions.
    """
    try:
        question = get_object_or_404(Question, pk=question_id)
        authorized_user = AuthorizedUser()

        if authorized_user.can_vote(request, question):
            authorized_user.submit_vote(request, question)
            messages.success(request, 'Vote has been successfully submitted.')
            return redirect(reverse('polls:results', args=(question.id,)))
        else:
            messages.error(request, "Voting on this poll is not allowed.")

    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        messages.error(request, "You didn't select a choice.")

    return redirect(reverse('polls:detail', args=(question.id,)))
