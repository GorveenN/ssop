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
    path('new_teacher/', views.new_teacher, name='new_teacher'),
    path('new_subject/', views.new_subject, name='new_subject'),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('add_subject/', views.add_subject, name='add_subject')
]
