from django.db import transaction
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.views.decorators.http import require_GET, require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.management.commands.download_teacher import download_teacher_info
from django.core.exceptions import PermissionDenied
from django.forms import formset_factory

from app.forms import *
from app.models import *


def get_fields(obj, fields):
    return {field: getattr(obj, field) for field in fields if hasattr(obj, field)}


def get_id(list):
    return [i.usos_id for i in list]


def group_by_letter(m):
    ALPHABET = '0123456789AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWXYZŹŻ'
    ret = {}
    for obj in m.objects.all():
        fl = str(obj)[0]
        if fl in ALPHABET:
            if fl in ret:
                ret[fl].append(obj)
            else:
                ret[fl] = [obj]
    return sorted(ret.items(), key=lambda i: ALPHABET.index(i[0]))


@require_GET
def ssop_home(request):
    return render(
        request,
        'ssop_home.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
        }
    )


def subject_page(request, subject_name): # TODO
    raise PermissionDenied
    # all_subjects = [
    #     get_fields(s, ['name', 'usos_link', 'usos_id'])
    #     for s in Subject.objects.all()
    # ]
    # if (sub_id in get_id(subjects)): # TODO nie działą jeszcze bo nie ma id
    #     dictionary['subject'] = Subject.objects.get(usos_id=sub_id).name
    #     comments = SubjectComment.objects.filter(subject=sub_id)
    #     comments = prepare_comments(comments)
    #     dictionary['comments'] = comments
    #     return render_to_response('subject.html', dictionary)
    # else:
    return render_to_response(
        'subject_page.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'surveyquestions': SubjectSurveyQuestion.objects.all()
        }
    )

@require_POST
def add_comment(request):
    sbj = get_object_or_404(Subject, usos_id=request.POST['subject_exact_id'])
    tcr = get_object_or_404(Teacher, usos_id=request.POST['teacher_id'])
    form = AddCommentForm(request.POST)

    with transaction.atomic():
        if form.is_valid():
            comment = form.save(commit=False)
            comment.teacher = tcr
            comment.subject_exact = sbj
            comment.save()

    return redirect(request.GET['redirect'])

@require_POST
def add_vote(request):
    response = redirect(request.GET['redirect'])

    with transaction.atomic():
        comment = get_object_or_404(TeacherComment, id=request.POST['comment_id'])
        if 'vote' in request.POST and request.POST['vote'] in ['+', '-']:
            new_vote = request.POST['vote']
            old_vote = request.COOKIES.get(f'tc-{comment.id}')

            if new_vote == old_vote:
                response.delete_cookie(f'tc-{comment.id}')
                if new_vote == '+':
                    comment.up_votes -= 1
                else:
                    comment.down_votes -= 1
            else:
                if request.POST['vote'] == '+':
                    comment.up_votes += 1
                    if old_vote is not None:
                        comment.down_votes -= 1
                    response.set_cookie(f'tc-{comment.id}', '+')
                else:
                    if old_vote is not None:
                        comment.up_votes -= 1
                    comment.down_votes += 1
                    response.set_cookie(f'tc-{comment.id}', '-')
        else:
            return HttpResponse("Unknown action", status=400)
        comment.save()

    return response


    que = TeacherSurveyQuestion.objects.all()
    StarsRatingFormSet = formset_factory(StarRatingForm, extra=len(que))
    add_comment_form = AddCommentForm()

    if request.method == 'POST':
        formset = StarsRatingFormSet(request.POST)
        print(request.POST)
        if formset.is_valid():
            #for item in formset:
            #    item.save(commit=True)
            print('Entered valid form')
    else:
        formset = StarsRatingFormSet()

    return render(
        request,
        'form_test.html',
        {
            'add_comment_form'  : add_comment_form,
            'managment_form'    : formset.management_form,
            'survey'            : zip(que, formset.forms),
            'all_subjects'      : group_by_letter(Subject),
            'all_teachers'      : group_by_letter(Teacher),
        }
    )



@require_GET
def teacher_page(request, usos_id):
    tcr = get_object_or_404(Teacher, usos_id=usos_id)
    sbj = get_object_or_404(Subject, name='Ogólne')
    comments = tcr.teachercomment_set.filter(subject=sbj, visible=True).order_by('-add_date')
    add_comment_form = AddCommentForm()

    que = TeacherSurveyQuestion.objects.all()
    factory = formset_factory(StarRatingForm, extra=len(que))
    formset = factory()

    return render(
        request,
        'teacher_page.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'teacher': tcr,
            'comments': comments,
            'subject': sbj,
            'add_comment_form': add_comment_form,
            'managment_form': formset.management_form,
            'survey': zip(que, formset.forms)
        }
    )

@require_GET
def teacher_comment_page(request, usos_id, subject):
    if subject == 'Ogólne':
        return redirect('teacher_page', usos_id=usos_id)

    tcr = get_object_or_404(Teacher, usos_id=usos_id)
    if subject == 'Wszystkie komentarze':
        sbj = subject
        que = {}
        man_form = {}
        survey = {}
        comments = tcr.teachercomment_set.filter(visible=True).order_by('-add_date')
    else:
        que = TeacherSurveyQuestion.objects.all()
        factory = formset_factory(StarRatingForm, extra=len(que))
        formset = factory()
        man_form = formset.management_form
        survey = zip(que, formset.forms)

        sbj = get_object_or_404(Subject, usos_id=subject)
        comments = tcr.teachercomment_set.filter(subject=sbj, visible=True).order_by('-add_date')
    add_comment_form = AddCommentForm()

    return render(
        request,
        'teacher_comment.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'teacher': tcr,
            'comments': comments,
            'subject': sbj,
            'add_comment_form': add_comment_form,
            'managment_form': man_form,
            'survey': survey
        }
    )


def rules_page(request):
    return render(
        request,
        'rules_page.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'teacher_id': request.GET['teacher']
        }
    )


@require_POST
@transaction.atomic
def report_comment(request):
    if any(x not in request.POST for x in ['content', 'comment_id', 'redirect']):
        return HttpResponse("Unknown action", status=400)

    cmt = get_object_or_404(TeacherComment, id=request.POST['comment_id'])
    report = Report(
        content = request.POST['content'],
        comment = cmt
    )
    report.save()

    # send an email
    subject = f'Zgłoszenie komentarza {cmt.id}'
    from_email = 'noreply@ssop-mim.pl'
    to_email = 'zglos@ssop-mim.pl'
    text_content = 'Ten mail został wygenerowany automatycznie. Nie odpowiadaj na niego!'
    html_content = render_to_string('report_mail.html', {'report': report})
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
        messages.success(request, 'Zgłoszono komentarz!')
    except:
        report.delete()
        messages.error(request, 'Nie udało się zgłosić komentarza, spróbuj ponownie!')
    return redirect(request.GET['redirect'])

@transaction.atomic
def report_handle(request, uuid):
    report = get_object_or_404(Report, uuid=uuid)
    if not report.done:
        if all(x in request.GET for x in ['accept', 'reject']) or all(x not in request.GET for x in ['accept', 'reject']):
            return HttpResponse("Unknown action", status=400)

        if 'accept' in request.GET:
            cmt = report.comment
            cmt.visible = False
            report.done = True
            cmt.save()
            report.save()
            messages.info(request, f'Zgłoszenie {report.uuid} zostało zaakceptowane!')
        elif 'reject' in request.GET:
            messages.info(request, f'Zgłoszenie {report.uuid} zostało odrzucone!')
            report.done = True
            report.save();
    else:
        messages.warning(request, f'Zgłoszenie {report.uuid} zostało już obsłużone!')

    return redirect('ssop_home')


def radio(request):
    que = TeacherSurveyQuestion.objects.all()
    StarsRatingFormSet = formset_factory(RateTeacherForm, extra=len(que))

    if request.method == 'POST':
        formset = StarsRatingFormSet(request.POST)
        print(request.POST)
        if formset.is_valid():
            for item in formset:
                item.save(commit=True)
            print('Entered valid form')
    else:
        formset = StarsRatingFormSet()

    return render(
        request,
        'radio.html',
        {
            'proper'        : formset,
            'managment_form': formset.management_form,
            'questions'    : TeacherSurveyQuestion.objects.all(),
            'map'          : zip(que, formset.forms),
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
        }
    )


def form_test(request):
    que = TeacherSurveyQuestion.objects.all()
    StarsRatingFormSet = formset_factory(StarRatingForm, extra=len(que))
    add_comment_form = AddCommentForm()

    if request.method == 'POST':
        formset = StarsRatingFormSet(request.POST)
        print(request.POST)
        if formset.is_valid():
            #for item in formset:
            #    item.save(commit=True)
            print('Entered valid form')
    else:
        formset = StarsRatingFormSet()

    return render(
        request,
        'form_test.html',
        {
            'add_comment_form'  : add_comment_form,
            'managment_form'    : formset.management_form,
            'survey'            : zip(que, formset.forms),
            'all_subjects'      : group_by_letter(Subject),
            'all_teachers'      : group_by_letter(Teacher),
        }
    )

@require_POST
def add_form_test(request):
    # sbj = get_object_or_404(Subject, usos_id=request.POST['subject_id'])
    # tcr = get_object_or_404(Teacher, usos_id=request.POST['teacher_id'])
    questions = len(TeacherSurveyQuestion.objects.all())
    factory = formset_factory(StarRatingForm, extra=questions)
    formset = factory(request.POST)

    print(request.POST)
    for idx, form in zip(range(0, questions), formset):
        with transaction.atomic():
            if form.is_valid():
                survey = TeacherSurveyAnswer()
                # survey.teacher = tcr
                # survey.subject = sbj
                survey.rating = form['rating']
                survey.question_id = request.POST["form-{}-question".format(idx)]
                survey.save()

    return redirect(request.GET['redirect'])

@require_POST
def add_subject_survey(request):
    # sbj = get_object_or_404(Subject, usos_id=request.POST['subject_id'])
    questions = len(SubjectSurveyQuestion.objects.all())
    factory = formset_factory(StarRatingForm, extra=questions)
    formset = factory(request.POST)

    print(request.POST)
    for idx, form in zip(range(0, questions), formset):
        with transaction.atomic():
            if form.is_valid():
                survey = SubjectSurveyAnswer()
                # survey.subject = sbj
                survey.rating = form['rating']
                survey.question_id = request.POST["form-{}-question".format(idx)]
                survey.save()

    return redirect(request.GET['redirect'])

@require_POST
def add_teacher_survey(request):
    print(request.POST)
    sbj = get_object_or_404(Subject, usos_id=request.POST['subject_id'])
    tcr = get_object_or_404(Teacher, usos_id=request.POST['teacher_id'])
    questions = len(TeacherSurveyQuestion.objects.all())
    factory = formset_factory(StarRatingForm, extra=questions)
    formset = factory(request.POST)

    print(request.POST)
    for idx, form in zip(range(0, questions), formset):
        with transaction.atomic():
            if form.is_valid():
                survey = TeacherSurveyAnswer()
                survey.teacher = tcr
                survey.subject = sbj
                survey.rating = form['rating'].value()
                survey.question_id = request.POST["form-{}-question".format(idx)]
                survey.save()

    return redirect(request.GET['redirect'])
