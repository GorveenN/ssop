from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('',                        views.ssop_home,    name='ssop_home'),
    path('teachers/<int:usos_id>',  views.teacher_page, name='teacher_page'),
    path('teachers/add_vote',  views.add_vote, name='add_vote'),
    path('teachers/add_comment',  views.add_comment, name='add_comment'),
    path('teachers/<int:usos_id>/<str:subject>', views.teacher_comment_page, name='teacher_comment_page'),
    path('subjects/<slug:subject_name>', views.subject_page, name='subject_page'), # TODO change to usos_id
    path('user_rules/',             views.rules_page,   name='rules_page'),
    path('report/',       views.report_comment, name='report_comment'),
    path('report/<slug:uuid>',      views.report_handle, name='report_handle'),
    path('radio/',      views.radio, name='radio'),
    path('form_test/',      views.form_test, name='form_test'),
    path('teachers/add_form_test/',      views.add_form_test, name='add_form_test'),
    path('teachers/add_teacher_survey/', views.add_teacher_survey, name='add_teacher_survey'),
    path('teachers/add_subject_survey/', views.add_subject_survey, name='add_subject_survey'),
]
