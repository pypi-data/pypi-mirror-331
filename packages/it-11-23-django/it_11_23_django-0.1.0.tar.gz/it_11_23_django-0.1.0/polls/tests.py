import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from . import models


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return models.Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_works_only_for_previous_dates(self):
        time = timezone.now() + datetime.timedelta(days=1)
        future_question = models.Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_returns_false_on_older_polls(self):
        time = timezone.now() - datetime.timedelta(days=5)
        old_question = models.Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_returns_true_on_recent_polls(self):
        time = timezone.now() - datetime.timedelta(days=4)
        recent_question = models.Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_shows_recent_poll(self):
        question = create_question("QuestionText", -2)
        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No recent polls...")
        self.assertContains(response, "Recent polls")
        self.assertContains(response, "QuestionText")

        self.assertQuerySetEqual(response.context["two_recent_questions"], [question])

    def test_shows_two_recent_polls(self):
        question_one = create_question("QuestionOne", -2)
        question_two = create_question("QuestionTwo", -3)
        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No recent polls...")
        self.assertContains(response, "Recent polls")
        self.assertContains(response, "QuestionOne")
        self.assertContains(response, "QuestionTwo")

        self.assertQuerySetEqual(
            response.context["two_recent_questions"], [question_one, question_two]
        )

    def test_no_polls(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No recent polls...")
        self.assertQuerySetEqual(response.context["two_recent_questions"], [])

    def test_future_polls(self):
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No recent polls...")
        self.assertQuerySetEqual(response.context["two_recent_questions"], [])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        self.assertEqual(response.status_code, 200)
