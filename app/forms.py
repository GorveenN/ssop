from django.forms import ModelForm
from django import forms
from .models import TeacherComment, Teacher, TeacherSurveyAnswer, SubjectSurveyAnswer, SubjectComment
from .models import *
from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, ModelSelect2MultipleWidget,
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

from .util import *


class AddCommentForm(ModelForm):
    class Meta:
        model = TeacherComment
        fields = ['content']
        labels = {
            'content': 'Opcjonalny komentarz',
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

class AddSubjectCommentForm(ModelForm):
    class Meta:
        model = SubjectComment
        fields = ['content']
        labels = {
            'content': 'Opcjonalny komentarz',
        }

    def __init__(self, *args, **kwargs):
        super(AddSubjectCommentForm, self).__init__(*args, **kwargs)
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


class SearchSubjectForm(forms.Form):
    name = forms.CharField(
        label='Wyszukiwana fraza:',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    min_ects = forms.ChoiceField(
        label='Minimalna liczba ects:',
        choices=ects_choices(),
        widget=Select2Widget(attrs={'class': 'form-control'}),
        required=False)

    max_ects = forms.ChoiceField(
        label='Maksymalna liczba ects:',
        choices=ects_choices(),
        widget=Select2Widget(attrs={'class': 'form-control'}),
        required=False)

    classType = forms.MultipleChoiceField(
        label='Rodzaj zajęć:',
        choices=make_choices(ClassType.objects.all()),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False)

    courseGroup = forms.MultipleChoiceField(
        label="Grupa przedmiotow:",
        choices=make_choices(CourseGroup.objects.all()),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False)

    courseLanguage = forms.MultipleChoiceField(
        label='Język:',
        choices=make_choices(CourseLanguage.objects.all()),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False)

    coursePeriod = forms.MultipleChoiceField(
        label='Semestr:',
        choices=make_choices(CoursePeriod.objects.all()),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False)

    courseType = forms.MultipleChoiceField(
        label='Typ przedmiotu:',
        choices=make_choices(CourseType.objects.all()),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False)


