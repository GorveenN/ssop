from django.db import transaction
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.views.decorators.http import require_GET, require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.management.commands.download_teacher import download_teacher_info
from django.core.exceptions import PermissionDenied

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
            'all_teachers': group_by_letter(Teacher)
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

@require_GET
def teacher_page(request, usos_id):
    tcr = get_object_or_404(Teacher, usos_id=usos_id)
    sbj = get_object_or_404(Subject, name='Ogólne')
    comments = tcr.teachercomment_set.filter(subject=sbj, visible=True).order_by('-add_date')
    add_comment_form = AddCommentForm()

    return render(
        request,
        'teacher_page.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'teacher': tcr,
            'comments': comments,
            'subject': sbj,
            'add_comment_form': add_comment_form
        }
    )

@require_GET
def teacher_comment_page(request, usos_id, subject):
    if subject == 'Ogólne':
        return redirect('teacher_page', usos_id=usos_id)

    tcr = get_object_or_404(Teacher, usos_id=usos_id)
    if subject == 'Wszystkie komentarze':
        sbj = subject
        comments = tcr.teachercomment_set.filter(visible=True).order_by('-add_date')
    else:
        sbj = get_object_or_404(Subject, usos_id=subject)
        clz = get_object_or_404(Class, teacher=usos_id, subject=sbj)
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
            'add_comment_form': add_comment_form
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


def new_teacher(request):
    add_comment_form = AddTeacherForm()
    return render(
        request,
        'new_teacher.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'add_comment_form' : add_comment_form
        }
    )


@require_POST
def add_teacher(request):
    form = AddTeacherForm(request.POST)
    with transaction.atomic():
        if form.is_valid():
            teacher = form.save(commit=False)
            info = download_teacher_info(form.cleaned_data['usos_id'])
            if (info):
                teacher.firstname, teacher.surname, teacher.website, teacher.email = info
                teacher.save()
                subject = Subject.objects.get(subject__name='Ogólne')
                clz = Class(teacher=teacher, subject=subject)
                clz.save()
                messages.success(request, f'Prowadzący {teacher.fullname} został dodany!')
                return redirect('ssop_home')
            else:
                messages.error(request, f'Nie udało się dodać prowadzącego!')
        else:
            add_comment_form = AddTeacherForm()
            messages.error(request, f'Podane USOS ID jest niepoprawne albo jest już na stronie!')
    return redirect('new_teacher')


def new_subject(request):
    add_comment_form = AddSubjectForm()
    return render(
        request,
        'new_subject.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'add_comment_form': add_comment_form
        }
    )


@require_POST
def add_subject(request): # TODO
    raise PermissionDenied
    return render_to_response(
        'ssop_home.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
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
