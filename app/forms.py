from django.forms import ModelForm
from django import forms
from .models import TeacherComment, Teacher, Subject, SurveyAnswer, TeacherSurveyAnswer


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


class RateTeacherForm2(forms.Form):
    rating = forms.ChoiceField(choices=[
        (1, ''),
        (2, ''),
        (3, ''),
        (4, ''),
        (5, ''),
    ], widget=forms.RadioSelect)


class RateTeacherForm1(forms.ModelForm):
    class Meta:
        model = TeacherSurveyAnswer
        fields = ['rating', 'question']
