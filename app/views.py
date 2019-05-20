import datetime

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
from django.db.models import Q
from django.db.models import Avg

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
    def top_list_len():
        return 10
    def clearing_function(top_list):
        return [element for element in top_list if element.average_rating() is not None and element.fullname != 'Ogólne']
    top_teachers = clearing_function(Teacher.objects.annotate(num=Avg('teachersurveyanswer__rating')).order_by('-num')[:top_list_len()])
    top_courses = clearing_function(Subject.objects.annotate(num=Avg('subjectsurveyanswer__rating')).order_by('-num')[:top_list_len()])

    return render(
        request,
        'ssop_home.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'top_teachers': top_teachers,
            'top_courses': top_courses,
        }
    )


@require_GET
def subject_page(request, usos_id):
    subject = get_object_or_404(Subject, usos_id=usos_id)
    comments = subject.subjectcomment_set.order_by('-add_date')

    comment_cookie_string = "sc-" + str(subject.usos_id) + "-edit"
    survey_cookie_string = "ss-" + str(subject.usos_id) + "-edit"
    if comment_cookie_string in request.COOKIES:
        comment_content = SubjectComment.objects.filter(pk=int(request.COOKIES[comment_cookie_string])).first().content
        add_comment_form = AddSubjectCommentForm(initial={"content": comment_content})
    else:
        add_comment_form = AddSubjectCommentForm()
    survey_questions = SubjectSurveyQuestion.objects.all()
    factory = formset_factory(StarRatingForm, extra=len(survey_questions))
    formset = factory()
    answers = [6] * len(formset.forms)
    if survey_cookie_string in request.COOKIES:
        i = 0
        ids = request.COOKIES[survey_cookie_string][1:].split("+")
        for rating_id in ids:
            filtered = SubjectSurveyAnswer.objects.filter(pk=int(rating_id))
            if filtered:
                answers[i] = filtered.first().rating
                i += 1

    all_questions = SubjectSurveyQuestion.objects.all()
    general_rating = [
        (question,
            SubjectSurveyAnswer.objects.filter(question=question, subject=subject.usos_id).aggregate(Avg('rating'))['rating__avg'])
        for question in all_questions]

    return render(
        request,
        'subject_page.html',
        {
            'subject': subject,
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'surveyquestions': SubjectSurveyQuestion.objects.all(),
            'comments': comments,
            'add_comment_form': add_comment_form,
            'managment_form': formset.management_form,
            'survey': zip(survey_questions, formset.forms, answers),
            'general_rating': general_rating
        }
    )


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


@require_POST
def add_subject_vote(request):
    response = redirect(request.GET['redirect'])

    with transaction.atomic():
        comment = get_object_or_404(SubjectComment, id=request.POST['comment_id'])
        if 'vote' in request.POST and request.POST['vote'] in ['+', '-']:
            new_vote = request.POST['vote']
            old_vote = request.COOKIES.get(f'sb-{comment.id}')

            if new_vote == old_vote:
                response.delete_cookie(f'sb-{comment.id}')
                if new_vote == '+':
                    comment.up_votes -= 1
                else:
                    comment.down_votes -= 1
            else:
                if request.POST['vote'] == '+':
                    comment.up_votes += 1
                    if old_vote is not None:
                        comment.down_votes -= 1
                    response.set_cookie(f'sb-{comment.id}', '+')
                else:
                    if old_vote is not None:
                        comment.up_votes -= 1
                    comment.down_votes += 1
                    response.set_cookie(f'sb-{comment.id}', '-')
        else:
            return HttpResponse("Unknown action", status=400)
        comment.save()

    return response


@require_GET
def teacher_page(request, usos_id):
    tcr = get_object_or_404(Teacher, usos_id=usos_id)
    comments = tcr.teachercomment_set.filter(visible=True).order_by('-add_date')
    add_comment_form = AddCommentForm()

    all_questions = TeacherSurveyQuestion.objects.all()
    factory = formset_factory(StarRatingForm, extra=len(all_questions))
    formset = factory()
    general_rating = [
        (question,
            TeacherSurveyAnswer.objects.filter(question=question, teacher=tcr).aggregate(Avg('rating'))['rating__avg'])
        for question in all_questions]

    return render(
        request,
        'teacher_page.html',
        {
            'all_subjects': group_by_letter(Subject),
            'all_teachers': group_by_letter(Teacher),
            'teacher': tcr,
            'comments': comments,
            'subject': 'Wszystkie komentarze',
            'add_comment_form': add_comment_form,
            'managment_form': formset.management_form,
            'survey': zip(all_questions, formset.forms),
            'general_rating': general_rating
        }
    )


@require_GET
def teacher_comment_page(request, usos_id, subject):
    if subject == 'Wszystkie komentarze':
        return redirect('teacher_page', usos_id=usos_id)

    tcr = get_object_or_404(Teacher, usos_id=usos_id)
    comment_cookie_string = "tc-" + str(tcr.usos_id) + "-" + subject + "-edit"
    survey_cookie_string = "ts-" + str(tcr.usos_id) + "-" + subject + "-edit"
    all_questions = TeacherSurveyQuestion.objects.all()
    factory = formset_factory(StarRatingForm, extra=len(all_questions))
    formset = factory()
    answers = [6] * len(formset.forms)
    if survey_cookie_string in request.COOKIES:
        i = 0
        ids = request.COOKIES[survey_cookie_string][1:].split("+")
        for rating_id in ids:
            filtered = TeacherSurveyAnswer.objects.filter(id=int(rating_id))
            if filtered:
                answers[i] = filtered.first().rating
                i += 1
    man_form = formset.management_form
    survey = zip(all_questions, formset.forms, answers)

    sbj = get_object_or_404(Subject, usos_id=subject)
    comments = tcr.teachercomment_set.filter(subject=sbj, visible=True).order_by('-add_date')

    general_rating = [
        (question,
            TeacherSurveyAnswer.objects.filter(question=question, teacher=tcr, subject=sbj).aggregate(Avg('rating'))['rating__avg'])
        for question in all_questions]

    if comment_cookie_string in request.COOKIES:
        comment_content = TeacherComment.objects.filter(pk=int(request.COOKIES[comment_cookie_string])).first().content
        add_comment_form = AddCommentForm(initial={'content': comment_content})
    else:
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
            'survey': survey,
            'general_rating': general_rating
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
            # 'previous_page': request.GET['previous_page']
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


@require_POST
def add_subject_survey(request):
    sbj = get_object_or_404(Subject, usos_id=request.POST['subject_id'])
    questions = len(SubjectSurveyQuestion.objects.all())
    factory = formset_factory(StarRatingForm, extra=questions)
    formset = factory(request.POST)
    comment_form = AddSubjectCommentForm(request.POST)
    survey_cookie_string = "ss-" + str(sbj.usos_id) + "-edit"
    comment_cookie_string = "sc-" + str(sbj.usos_id) + "-edit"
    edit_expiry_time = 365 * 24 * 60 * 60  # 1 year
    set_survey_cookie = False
    set_comment_cookie = False
    survey_ids = ""

    with transaction.atomic():
        if comment_form.is_valid():
            if comment_cookie_string not in request.COOKIES:
                comment = comment_form.save(commit=False)
                comment.subject = sbj
                if comment.content:
                    comment.save()
                    comment_id = str(comment.pk)
                    set_comment_cookie = True
            else:
                comment_to_edit = SubjectComment.objects.filter(pk=int(request.COOKIES[comment_cookie_string])).first()
                comment_to_edit.content = comment_form.save(commit=False).content
                if (datetime.datetime.now().replace(tzinfo=None) - comment_to_edit.add_date.replace(tzinfo=None)) \
                        > datetime.timedelta(minutes=2):
                    comment_to_edit.edited = True
                comment_to_edit.save()

    if survey_cookie_string in request.COOKIES:
        i = 0
        ids = request.COOKIES[survey_cookie_string][1:].split("+")

    for idx, form in zip(range(0, questions), formset):
        with transaction.atomic():
            if form.is_valid():
                if survey_cookie_string in request.COOKIES:
                    SubjectSurveyAnswer.objects.filter(pk=int(ids[i])).update(rating=form["rating"].value())
                    i += 1
                else: #new entry
                    set_survey_cookie = True
                    survey = SubjectSurveyAnswer()
                    survey.subject = sbj
                    survey.rating = form['rating'].value()
                    survey.question_id = request.POST["form-{}-question".format(idx)]
                    survey.save()
                    survey_ids += "+" + str(survey.pk)

    response = redirect(request.GET['redirect'])

    if set_survey_cookie:
        response.set_cookie(key=survey_cookie_string, value=survey_ids, max_age=edit_expiry_time)

    if set_comment_cookie:
        response.set_cookie(key=comment_cookie_string, value=comment_id, max_age=edit_expiry_time)

    return response

@require_POST
def add_teacher_survey(request):
    sbj = get_object_or_404(Subject, usos_id=request.POST['subject_id'])
    tcr = get_object_or_404(Teacher, usos_id=request.POST['teacher_id'])
    questions = len(TeacherSurveyQuestion.objects.all())
    factory = formset_factory(StarRatingForm, extra=questions)
    formset = factory(request.POST)
    comment_form = AddCommentForm(request.POST)
    survey_cookie_string = "ts-" + str(tcr.usos_id) + "-" + str(sbj.usos_id) + "-edit"
    comment_cookie_string = "tc-" + str(tcr.usos_id) + "-" + str(sbj.usos_id) + "-edit"
    edit_expiry_time = 365 * 24 * 60 * 60  # 1 year
    set_survey_cookie = False
    set_comment_cookie = False
    survey_ids = ""

    with transaction.atomic():
        if comment_form.is_valid():
            if comment_cookie_string not in request.COOKIES:
                comment = comment_form.save(commit=False)
                comment.teacher = tcr
                comment.subject = sbj
                if comment.content:
                    comment.save()
                    comment_id = str(comment.pk)
                    set_comment_cookie = True
            else:
                comment_to_edit = TeacherComment.objects.filter(pk=int(request.COOKIES[comment_cookie_string])).first()
                comment_to_edit.content = comment_form.save(commit=False).content
                if (datetime.datetime.now().replace(tzinfo=None) - comment_to_edit.add_date.replace(tzinfo=None))\
                        > datetime.timedelta(minutes=2):
                    comment_to_edit.edited = True
                comment_to_edit.save()

    if survey_cookie_string in request.COOKIES:
        i = 0
        ids = request.COOKIES[survey_cookie_string][1:].split("+")

    for idx, form in zip(range(0, questions), formset):
        with transaction.atomic():
            if form.is_valid():
                if survey_cookie_string in request.COOKIES:
                    TeacherSurveyAnswer.objects.filter(pk=int(ids[i])).update(rating=form["rating"].value())
                    i += 1

                else: #new entry
                    set_survey_cookie = True
                    survey = TeacherSurveyAnswer()
                    survey.teacher = tcr
                    survey.subject = sbj
                    survey.rating = form['rating'].value()
                    survey.question_id = request.POST["form-{}-question".format(idx)]
                    survey.save()
                    survey_ids += "+" + str(survey.pk)

    response = redirect(request.GET['redirect'])

    if set_survey_cookie:
        response.set_cookie(key=survey_cookie_string, value=survey_ids, max_age=edit_expiry_time)

    if set_comment_cookie:
        response.set_cookie(key=comment_cookie_string, value=comment_id, max_age=edit_expiry_time)

    return response


def search(request):
    html_data = {
                'all_subjects': group_by_letter(Subject),
                'all_teachers': group_by_letter(Teacher)
            }

    if request.method == 'POST' and SearchSubjectForm(request.POST).is_valid():
        print(request.POST)

        Qs = {
            'name': Q(),
            'ects': Q(),
            'courseLanguage': Q(),
            'coursePeriod': Q(),
            'courseType': Q(),
            'courseGroup': Q(),
            'classType': Q()
        }

        if request.POST['name'] != '':
            Qs['name'] |= Q(name__contains=request.POST['name'])
            Qs['name'] |= Q(usos_id__contains=request.POST['name'])

        if request.POST['max_ects'] != '':
            Qs['ects'] &= Q(ects__lt=float(request.POST['max_ects']))

        if request.POST['min_ects'] != '':
            Qs['ects'] &= Q(ects__gt=float(request.POST['min_ects']))

        if 'courseLanguage' in request.POST:
            for item in request.POST.getlist('courseLanguage'):
                Qs['courseLanguage'] |= Q(language=escape_string(item))

        if 'coursePeriod' in request.POST:
            for item in request.POST.getlist('coursePeriod'):
                Qs['coursePeriod'] |= Q(period=escape_string(item))

        if 'courseType' in request.POST:
            for item in request.POST.getlist('courseType'):
                Qs['courseType'] |= Q(type_of_course=escape_string(item))

        if 'courseGroup' in request.POST:
            for item in request.POST.getlist('courseGroup'):
                print(json.dumps(item))
                Qs['courseGroup'] |= Q(groups_of_courses__contains=escape_string(item))

        if 'classType' in request.POST:
            for item in request.POST.getlist('classType'):
                Qs['classType'] |= Q(types_of_classes__contains=escape_string(item))

        masterQ = Q()
        for key, value in Qs.items():
            masterQ &= value
        subjects = Subject.objects.all().filter(masterQ)
        print(masterQ)
        print(subjects)

        html_data['queried_sub'] = subjects
        if len(subjects) == 0:
            html_data['queried_sub'] = 'Empty'
        html_data['form'] = SearchSubjectForm()
        return render(request, 'search_page.html', html_data)

    html_data['queried_sub'] = None
    html_data['form'] = SearchSubjectForm()
    return render(request, 'search_page.html', html_data)

