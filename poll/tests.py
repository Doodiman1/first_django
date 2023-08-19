import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question("Future Question", 30)
        url = reverse("poll:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question("Past Question", -10)
        url = reverse("poll:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)




class QuestionModelTests(TestCase):

    def test_no_questions(self):
        response = self.client.get(reverse("poll:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Polls Available")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
    
    def test_past_question(self):
        question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("poll:index"))
        self.assertQuerySetEqual(
                response.context["latest_question_list"],
                [question]
           )

    def test_future_question(self):
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("poll:index"))
        self.assertContains(response, "No Polls Available")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_and_past_questions(self):
        question = create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("poll:index"))
        self.assertQuerySetEqual(
                response.context["latest_question_list"],
                [question]
                )

    def test_two_past_questions(self):
        question1 = create_question(question_text="Past Question 1", days=-1)
        question2 = create_question(question_text="Past Question 2", days=-100)
        response = self.client.get(reverse("poll:index"))
        self.assertQuerySetEqual(
                response.context["latest_question_list"],
                [question2, question1]
                )

    
    def test_was_published_recently_is_future_question(self):
        # Testing if a question that has been made in the future
        # Returns True when function was_published_recently is run

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        # Function should return False for published dates > 1 day
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_new_question(self):
        time = timezone.now() -datetime.timedelta(hours=23, minutes =59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


