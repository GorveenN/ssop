from django.core.management.base import BaseCommand
from app.models import *
import json


def load_json(filename):
    return json.load(open(filename))


def save_json(jason, filename):
    json.dump(jason, open(filename, 'w'), indent=4)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Populate database by usos data.'
        parser.add_argument('--map', type=str)
        parser.add_argument('--usos', type=str,)
        parser.add_argument('--wikispaces', type=str,)

    def handle(self, *args, **options):
        usos_json = load_json(options['usos'])
        wikispaces_json = load_json(options['wikispaces'])

        mapping = dict()
        for subject in load_json(options['map']):
            mapping[str(subject['from'])] = subject['to']

        usos_json['0'] = {
            "name": "Ogólne",
            "lecturers": {}
            }

        comments_wikispaces = []
        lecturers_wikispaces = dict()

        for teacher in wikispaces_json:
            if teacher['model'] == "app.teacher":
                lecturers_wikispaces[str(teacher['pk'])] = {
                    "firstname": teacher['fields']['firstname'],
                    "surname": teacher['fields']['surname'],
                    "website": None,
                    "email": None
                }
            elif teacher['model'] == "app.teachercomment":
                comments_wikispaces += [{
                    "teacher": teacher['fields']['teacher'],
                    "subject": mapping[str(teacher['fields']['subject_exact'])],
                    "content": teacher['fields']['content'],
                    "add_date": teacher['fields']['add_date'],
                    "wikispaces": teacher['fields']['wikispaces'],
                    "up_votes": teacher['fields']['up_votes'],
                    "down_votes": teacher['fields']['down_votes'],
                    "visible": teacher['fields']['visible'],
                }]

                usos_json[str(mapping[str(teacher['fields']['subject_exact'])])]['lecturers'][str(teacher['fields']['teacher'])] = {
                    "firstname": lecturers_wikispaces[str(teacher['fields']['teacher'])]['firstname'],
                    "surname": lecturers_wikispaces[str(teacher['fields']['teacher'])]['surname'],
                    "website": None,
                    'email': None
                }

        lecturer_objects = dict()
        subject_objects = dict()

        for subject_id, subject_info in usos_json.items():
            subject_objects[subject_id] = Subject(usos_id=subject_id,
                                                  name=subject_info['name']
                                                  )
            subject_objects[subject_id].save()
            print(subject_id)

            for lecturer_id, lecturer_info in subject_info['lecturers'].items():
                if lecturer_id not in lecturer_objects:
                    lecturer_objects[lecturer_id] = Teacher(
                        usos_id=lecturer_id,
                        firstname=lecturer_info['firstname'],
                        surname=lecturer_info['surname'],
                        website=None,
                        email=None
                    )
                    lecturer_objects[lecturer_id].save()

                Class(teacher=lecturer_objects[lecturer_id],
                      subject=subject_objects[subject_id]
                      ).save()

        for comment in comments_wikispaces:
            TeacherComment(teacher=lecturer_objects[str(comment['teacher'])],
                           subject=subject_objects[comment['subject']],
                           content=comment['content'],
                           add_date=comment['add_date'],
                           wikispaces=comment['wikispaces'],
                           up_votes=comment['up_votes'],
                           down_votes=comment['down_votes'],
                           visible=comment['visible']
                           ).save()