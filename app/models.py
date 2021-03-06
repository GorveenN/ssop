import uuid
from django.db import models
from jsonfield import JSONField
from pytz import timezone
import statistics

USOS_TEACHER_TMPL = "https://usosweb.mimuw.edu.pl/kontroler.php?_action=actionx:katalog2/osoby/pokazOsobe%28os_id:"
USOS_SUBJ_TMPL = "https://usosweb.mimuw.edu.pl/kontroler.php?_action=katalog2/przedmioty/pokazPrzedmiot&kod="


class Teacher(models.Model):
    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ['surname']

    firstname = models.CharField(max_length=64)
    surname   = models.CharField(max_length=64)
    usos_id   = models.IntegerField(primary_key=True)
    website   = models.CharField(max_length=64, null=True)
    email     = models.CharField(max_length=64, null=True)
    ordering = ['surname']

    @property
    def fullname(self):
        return f'{self.surname} {self.firstname}'

    @property
    def usos_link(self):
        return USOS_TEACHER_TMPL + str(self.usos_id)

    def __str__(self):
        return self.fullname

    @property
    def comments(self):
        return self.teachercomment_set.all().order_by('-add_date')

    @property
    def classes(self):
        return [s.subject for s in self.class_set.all()]

    @property
    def info(self):
        return {
            'usos_link': USOS_TEACHER_TMPL + str(self.usos_id),
            'fullname': self.fullname,
            'web_link': '',
            'usos_id': self.usos_id
        }

    def average_rating(self):
        all_questions = TeacherSurveyQuestion.objects.all()
        rating = [TeacherSurveyAnswer.objects.filter(question=question, teacher=self)
                               .aggregate(models.Avg('rating'))['rating__avg'] for question in all_questions]
        return None if None in rating else statistics.mean(rating)


class Subject(models.Model):
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    usos_id             = models.CharField(max_length=32, primary_key=True)
    name                = models.CharField(max_length=64)
    ects                = models.FloatField(default=None, null=True)
    language            = models.CharField(max_length=32, default=None, null=True)
    period              = models.CharField(max_length=32, default=None, null=True)
    # types             = JSONField(default=None, null=True)
    type_of_course      = models.CharField(max_length=32, default=None, null=True)
    groups_of_courses   = JSONField(default=None, null=True)
    types_of_classes    = JSONField(default=None, null=True)

    @property
    def usos_link(self):
        return USOS_SUBJ_TMPL + str(self.usos_id)

    @property
    def fullname(self):
        return f'{self.name}'

    @property
    def teachers(self):
        return [entry.teacher for entry in self.class_set.all()]

    def average_rating(self):
        all_questions = SubjectSurveyQuestion.objects.all()
        rating = [SubjectSurveyAnswer.objects.filter(question=question, subject=self)
                      .aggregate(models.Avg('rating'))['rating__avg'] for question in all_questions]
        return None if None in rating else statistics.mean(rating)

    def __str__(self):
        return f'{self.name}'


class Class(models.Model):
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        unique_together = ('teacher', 'subject')

    teacher = models.ForeignKey(Teacher, on_delete = models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.teacher} - {self.subject}'


class Comment(models.Model):
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        abstract = True

    subject       = models.ForeignKey(Subject, on_delete = models.CASCADE)
    content       = models.TextField()
    add_date      = models.DateTimeField(auto_now_add=True)
    up_votes   = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)
    edited = models.BooleanField(default=False)

    @property
    def add_date_pretty(self):
        edited = " (edytowany)" if self.edited else ""
        return self.add_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S") + edited

    @property
    def votes_result(self):
        return self.up_votes - self.down_votes


class TeacherComment(Comment):
    class Meta:
        verbose_name = "Teacher comment"
        verbose_name_plural = "Teacher comments"

    teacher       = models.ForeignKey(Teacher, on_delete = models.CASCADE)
    wikispaces    = models.BooleanField(default=False)
    visible       = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.add_date_pretty} | {self.subject} - {self.teacher.fullname}'


class SubjectComment(Comment):
    class Meta:
        verbose_name = "Subject comment"
        verbose_name_plural = "Subject comments"

    def __str__(self):
        return f'{self.add_date_pretty}: {self.subject}'


class Report(models.Model):
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    uuid     = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment  = models.ForeignKey(TeacherComment, on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True)
    content  = models.TextField()
    done     = models.BooleanField(default=False)

    @property
    def add_date_pretty(self):
        return self.add_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S")


# Not so sure that it should be stored here
class SurveyQuestion(models.Model):
    class Meta:
        verbose_name = "Survey question"
        verbose_name_plural = "Survey questions"
        abstract = True

    question_text = models.CharField(max_length = 100)

    def __str__(self):
        return self.question_text


class TeacherSurveyQuestion(SurveyQuestion):
    class Meta:
        verbose_name = "Teacher  survey question"
        verbose_name_plural = "Teacher survey questions"


class SubjectSurveyQuestion(SurveyQuestion):
    class Meta:
        verbose_name = "Subject survey question"
        verbose_name_plural = "Subject survey questions"


class SurveyAnswer(models.Model):
    class Meta:
        abstract = True

    rating = models.IntegerField(null=False)


class SubjectSurveyAnswer(SurveyAnswer):
    class Meta:
        verbose_name = "Subject survey answer"
        verbose_name_plural = "Subject survey answer"

    question = models.ForeignKey(SubjectSurveyQuestion, models.CASCADE)
    subject = models.ForeignKey(Subject, models.CASCADE)


class TeacherSurveyAnswer(SurveyAnswer):
    class Meta:
        verbose_name = "Teacher survey answer"
        verbose_name_plural = "Teacher survey answer"

    question = models.ForeignKey(TeacherSurveyQuestion, models.CASCADE)
    teacher = models.ForeignKey(Teacher, models.CASCADE)
    subject = models.ForeignKey(Subject, models.CASCADE)


class StringArray(models.Model):
    class Meta:
        ordering = ['name']
        abstract = True

    name = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.name


class CourseLanguage(StringArray):pass
class CoursePeriod(StringArray):pass
class CourseType(StringArray):pass
class CourseGroup(StringArray):pass
class ClassType(StringArray):pass

