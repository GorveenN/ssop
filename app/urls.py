from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('',                        views.ssop_home,    name='ssop_home'),
    path('teachers/<int:usos_id>',  views.teacher_page, name='teacher_page'),
    path('teachers/add_vote',  views.add_vote, name='add_vote'),
    path('teachers/add_comment',  views.add_comment, name='add_comment'),
    path('teachers/<int:usos_id>/<str:subject>', views.teacher_comment_page, name='teacher_comment_page'),
    path('subjects/add_subject_comment', views.add_subject_comment, name='add_subject_comment'),
    path('subjects/add_subject_vote', views.add_subject_vote, name='add_subject_vote'),
    path('subjects/<str:usos_id>', views.subject_page, name='subject_page'), # TODO problem: it shouldn't be a string, but
    # int obviously doesn't work and slug / uuid seems to fail as well :/
    path('user_rules/',             views.rules_page,   name='rules_page'),
    path('report/',       views.report_comment, name='report_comment'),
    path('report/<slug:uuid>',      views.report_handle, name='report_handle'),
    path('teachers/add_teacher_survey/', views.add_teacher_survey, name='add_teacher_survey'),
    path('subjects/add_subject_survey/', views.add_subject_survey, name='add_subject_survey'),
    path('search/', views.search, name='search')
]
