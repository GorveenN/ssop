import json
from django.db import transaction
from django.core.management.base import BaseCommand
from app.models import *

#TODO przdzielanie ID
def get_subject_id(subject_name):
    return "default_usos_id"

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Populates database with JSON data'
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-a',
            '--arg-input',
            type=str,
            help='hardcoded JSON data'
        )
        group.add_argument(
            '-f',
            '--file-input',
            type=str,
            help='file with JSON data'
        )

    def handle(self, *args, **options):
        print('Reading JSON data...', end='', flush=True)
        if options['arg_input']:
            page_json_str = options['arg_input']
        elif options['file_input']:
            with open(options['file_input'], 'r') as f:
                page_json_str = f.read()
        dicted_page = json.loads(page_json_str)
        print('done')

        print('Populating db with JSON data...', end='', flush=True)
        with transaction.atomic():
            for usos_id, data in dicted_page.items():
                teacher = Teacher(
                    firstname = data['imie'],
                    surname   = data['nazwisko'],
                    usos_id   = usos_id
                )
                teacher.save()

                for comment in data['komentarze']:
                    subject_name = comment['przedmiot_nazwa']
                    subject_id = None
                    subject_obj = Subject.objects.filter(name=subject_name)

                    if not subject_obj.exists():
                        subject = Subject(
                            usos_id = subject_id,
                            name    = subject_name
                        )
                        subject.save()
                    else:
                        subject = subject_obj.first()

                    subject_exact_obj = SubjectExact.objects.filter(subject=subject)
                    if not subject_exact_obj.exists():
                        subject_exact = SubjectExact(
                            subject = subject
                        )
                        subject_exact.save()
                    else:
                        subject_exact = subject_exact_obj.first()

                    if not Class.objects.filter(teacher=teacher, subject_exact=subject_exact).exists():
                        _class = Class(
                            teacher       = teacher,
                            subject_exact = subject_exact
                        )
                        _class.save()

                    teacher_comment = TeacherComment(
                        teacher       = teacher,
                        subject_exact = subject_exact,
                        content       = comment['tresc'],
                        wikispaces    = True
                    )
                    teacher_comment.save()
        print('done')
