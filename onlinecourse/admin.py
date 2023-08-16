from django.contrib import admin
# <HINT> Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# <HINT> Register QuestionInline and ChoiceInline classes here


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4


class QuesitoninLine(admin.StackedInline):
    model = Question
    inlines = [ChoiceInline]
    extra = 2


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuesitoninLine]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['question_text', 'grade']
    search_fields = ['question_text']
    list_filter = ['grade']


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'is_correct']
    list_filter = ['is_correct']
    search_fields = ['choice_text']


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'id']
    search_fields = ['enrollment__user__username']
    list_filter = ['enrollment__course']

# <HINT> Register Question and Choice models here


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission, SubmissionAdmin)
