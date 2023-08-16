from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(
            user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def extract_answers(request):
    submitted_anwsers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    return submitted_anwsers


@login_required
def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    submission = Submission.objects.create(enrollment=enrollment)

    selected_choice_ids = extract_answers(request)

    for choice_id in selected_choice_ids:
        choice = get_object_or_404(Choice, id=choice_id)
        submission.choices.add(choice)

    return redirect('onlinecourse:show_exam_result',
                    course_id=course.id,
                    submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)
    user = request.user

    selected_choices = submission.choices.all()

    total_points = 0
    total_grade = 0

    for question in course.question_set.all():
        correct_choices = question.choice_set.filter(is_correct=True)
        grade_per_correct_choice = question.grade / correct_choices.count()

        question_points = 0

        # Add points for each correct choice selected by the user
        for choice in correct_choices:
            if choice in selected_choices:
                question_points += grade_per_correct_choice

        # Deduct points for any incorrect choice selected by the user
        incorrect_choices_selected = selected_choices.filter(question=question,
                                                             is_correct=False).count()

        # I deduct half marks of a question in case it's incorrectly selected
        question_points -= incorrect_choices_selected * \
            (grade_per_correct_choice / 2)

        # Ensure that the grade for a question doesn't go negative
        question_points = max(0, question_points)

        total_points += question_points
        total_grade += question.grade

    score = round((total_points / total_grade) * 100.00, 2)

    passed = False

    # Assuming 80% is the passing score
    if float(score) >= 80.0:
        passed = True

    context = {
        'user': user,
        'course': course,
        'selected_choices': selected_choices,
        'score': score,
        'passed': passed
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
