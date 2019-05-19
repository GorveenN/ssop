from django.forms import ModelForm
from django import forms
from .models import TeacherComment, Teacher, TeacherSurveyAnswer, SubjectSurveyAnswer
from .models import *


class AddCommentForm(ModelForm):
    class Meta:
        model = TeacherComment
        fields = ['content']
        labels = {
            'content': 'Treść komentarza',
        }

    def __init__(self, *args, **kwargs):
        super(AddCommentForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })
        self.fields['content'].required = False
        self.fields['content'].widget.attrs.update({
            'style':'resize:none;'
        })


class AddTeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ['usos_id']
        labels = {
            'usos_id': 'Podaj USOS ID prowadzącego:',
        }

    def __init__(self, *args, **kwargs):
        super(AddTeacherForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })
        self.fields['usos_id'].widget.attrs.update({
            'style':'resize:none;',
            'min': 0
        })


class AddSubjectForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ['usos_id']
        labels = {
            'usos_id': 'Podaj USOS ID przedmiotu:',
        }
    #
    def __init__(self, *args, **kwargs):
        super(AddSubjectForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'min': 0
            })
        self.fields['usos_id'].widget.attrs.update({
            'style':'resize:none;'
        })


class StarRatingForm(forms.Form):
    choices = (
        (5, 5),
        (4, 4),
        (3, 3),
        (2, 2),
        (1, 1),
    )

    rating = forms.ChoiceField(choices=choices, widget=forms.RadioSelect())


class RateTeacherForm(forms.ModelForm):
    class Meta:
        model = TeacherSurveyAnswer
        fields = ['rating', 'question']


class RateSubjectForm(forms.ModelForm):
    class Meta:
        model = SubjectSurveyAnswer
        fields = ['rating', 'question']


def make_choices(objects):
    choices = ()
    for item in objects:
        choices += ((item.name, item.name),)
    return choices


class SearchSubjectForm(forms.Form):
    name = forms.CharField(required=False)
    min_ects = forms.FloatField(required=False)
    max_ects = forms.FloatField(required=False)

    classType = forms.MultipleChoiceField(
        choices=make_choices(ClassType.objects.all()),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    courseGroup =  forms.MultipleChoiceField(
        choices=make_choices(CourseGroup.objects.all()),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    courseLanguage =  forms.MultipleChoiceField(
        choices=make_choices(CourseLanguage.objects.all()),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    coursePeriod =  forms.MultipleChoiceField(
        choices=make_choices(CoursePeriod.objects.all()),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    courseType =  forms.MultipleChoiceField(
        choices=make_choices(CourseType.objects.all()),
        widget=forms.CheckboxSelectMultiple,
        required=False)

