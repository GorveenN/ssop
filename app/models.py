import uuid
from django.db import models
from datetime import datetime
from pytz import timezone

USOS_TEACHER_TMPL = "https://usosweb.mimuw.edu.pl/kontroler.php?_action=actionx:katalog2/osoby/pokazOsobe%28os_id:"
USOS_SUBJ_TMPL = "https://usosweb.mimuw.edu.pl/kontroler.php?_action=katalog2/przedmioty/pokazPrzedmiot&kod="

class Teacher(models.Model):
    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    firstname = models.CharField(max_length=64)
    surname   = models.CharField(max_length=64)
    usos_id   = models.IntegerField(primary_key=True)
    website   = models.CharField(max_length=64, null=True, default=None)
    email     = models.CharField(max_length=64, null=True, default=None)

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
        return [s.subject_exact for s in self.class_set.all()]

    @property
    def info(self):
        return {
            'usos_link': USOS_TEACHER_TMPL + str(self.usos_id),
            'fullname': self.fullname,
            'web_link': '',
            'usos_id': self.usos_id
        }

    class Meta:
        ordering = ['surname']

class Subject(models.Model):
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    usos_id = models.CharField(max_length=32, primary_key=True)
    name    = models.CharField(max_length=64)

    @property
    def usos_link(self):
        return USOS_SUBJ_TMPL + str(self.usos_id)

    def __str__(self):
        return f'{self.name}'


class TeacherComment(models.Model):
    class Meta:
        verbose_name = "Teacher comment"
        verbose_name_plural = "Teacher comments"

    teacher       = models.ForeignKey(Teacher, on_delete = models.CASCADE)
    subject       = models.ForeignKey(Subject, on_delete = models.CASCADE)
    content       = models.TextField()
    add_date      = models.DateTimeField(auto_now_add=True)
    wikispaces    = models.BooleanField(default=False)
    up_votes      = models.IntegerField(default=0)
    down_votes    = models.IntegerField(default=0)
    visible       = models.BooleanField(default=True)

    @property
    def votes_result(self):
        return self.up_votes - self.down_votes

    @property
    def add_date_pretty(self):
        return self.add_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        if self.wikispaces:
            return f'{self.add_date_pretty} | (OLD) {self.subject_exact} - {self.teacher.fullname}'
        else:
            return f'{self.add_date_pretty} | {self.subject_exact} - {self.teacher.fullname}'

class SubjectComment(models.Model):
    class Meta:
        verbose_name = "Subject comment"
        verbose_name_plural = "Subject comments"

    subject    = models.ForeignKey(Subject, on_delete=models.CASCADE)
    content    = models.TextField()
    add_date   = models.DateTimeField(auto_now_add=True)
    up_votes   = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)

    @property
    def add_date_pretty(self):
        return self.add_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def votes_result(self):
        return self.up_votes - self.down_votes

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
