from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from . import models


class IndexView(generic.ListView):
    context_object_name = "two_recent_questions"

    def get_queryset(self):
        return models.Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date"
        )[:2]


class DetailView(generic.DetailView):
    pk_url_kwarg = "question_id"

    def get_queryset(self):
        return models.Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    template_name = "polls/results.html"
    model = models.Question
    context_object_name = "question_results"
    pk_url_kwarg = "question_id"


def vote(request, question_id):
    question = get_object_or_404(models.Question, id=question_id)
    try:
        selected_choice_id = request.POST.get("choice")
        selected_choice = question.choice_set.get(id=selected_choice_id)
    except (KeyError, models.Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {"question": question, "error_message": "No choice selected"},
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question_id,)))
