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
                    "subject": mapping[int(teacher['fields']['subject_exact'])],
                    "content": teacher['fields']['content'],
                    "add_date": teacher['fields']['add_date'],
                    "wikispaces": teacher['fields']['wikispaces'],
                    "up_votes": teacher['fields']['up_votes'],
                    "down_votes": teacher['fields']['down_votes'],
                    "visible": teacher['fields']['visible'],
                }]

                usos_json[mapping[teacher['fields']['subject_exact']]]['lecturers'][teacher['fields']['teacher']] = {
                    "firstname": lecturers_wikispaces[teacher['fields']['teacher']]['firstname'],
                    "surname": lecturers_wikispaces[teacher['fields']['teacher']]['surname'],
                    "website": None,
                    "email": None
                }

        lecturer_objects = dict()
        subject_objects = dict()

        for subject_id, subject_info in usos_json.items():
            subject_objects[subject_id] = Subject(usos_id=subject_id,
                                                  name=subject_info['name']
                                                  )
            subject_objects[subject_id].save()

            for lecturer_id, lecturer_info in subject_info['teachers'].items():
                if lecturer_id not in lecturer_objects:
                    lecturer_objects[lecturer_id] = Teacher(
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
            TeacherComment(teacher=lecturer_objects[comment['teacher']],
                           subject=subject_objects[comment['subject']],
                           content=comment['content'],
                           add_date=comment['add_date'],
                           wikispaces=comment['wikispaces'],
                           up_votes=comment['up_votes'],
                           down_votes=comment['down_votes'],
                           visible=comment['visible']
                           ).save()

# class Command(BaseCommand):
#
#     def add_arguments(self, parser):
#         parser.help = 'Populate database by usos data.'
#         parser.add_argument('--map', type=str)
#         parser.add_argument('--usos', type=str,)
#         parser.add_argument('--wikispaces', type=str,)
#
#     def handle(self, *args, **options):
#         usos_subjects = load_json(options['usos_subjects'])
#         usos_teachers = load_json(options['usos_teachers'])
#         wikispaces_data = load_json(options['wikispaces'])
#         map = load_json(options['map'])
#
#         mapping = dict()
#         for subject in map:
#             mapping[str(subject['from'])] = subject['to']
#
#
#
#         new_subjects = {}
#         for subject in usos_subjects:
#             new_subjects[subject['id']] = dict()
#             new_subjects[subject['id']]['name'] =  subject['name']
#             new_subjects[subject['id']]['lecturers'] =  [int(x) for x in subject['lecturers']]
#         print(new_subjects)
#
#         new_comments = []
#         print(mapping)
#         new_teachers = {}
#         for teacher in wikispaces_data:
#             if teacher['model'] == "app.teacher":
#                 new_teachers[int(teacher['pk'])] = \
#                     Teacher(firstname=teacher['fields']['firstname'],
#                             surname=teacher['fields']['surname'],
#                             usos_id=int(teacher['pk']),
#                             website=teacher['fields']['website'],
#                             email=teacher['fields']['email']
#                             )
#                 new_teachers[int(teacher['pk'])].save()
#             elif teacher['model'] == "app.teachercomment":
#                 new_comment = {}
#                 print(teacher['fields']['teacher'])
#                 print(mapping[int(teacher['fields']['subject_exact'])])
#                 new_subjects[mapping[int(teacher['fields']['subject_exact'])]]['lecturers'] += [teacher['fields']['teacher']]
#                 new_comment['teacher'] = teacher['fields']['teacher']
#                 new_comment['subject'] = mapping[int(teacher['fields']['subject_exact'])]
#                 new_comment['content'] = teacher['fields']['content']
#                 new_comment['add_date'] = teacher['fields']['add_date']
#                 new_comment['wikispaces'] = teacher['fields']['wikispaces']
#                 new_comment['up_votes'] = teacher['fields']['up_votes']
#                 new_comment['down_votes'] = teacher['fields']['down_votes']
#                 new_comment['visible'] = teacher['fields']['visible']
#                 new_comments += [new_comment]
#
#         for teacher in usos_teachers:
#             new_teachers[int(teacher['pk'])] = \
#                 Teacher(firstname=teacher['fields']['firstname'],
#                     surname=teacher['fields']['surname'],
#                     usos_id=int(teacher['pk']),
#                     website=None, email=None
#                     )
#             new_teachers[int(teacher['pk'])].save()
#
#         added_subjects = {}
#         for sub_id, sub_val in new_subjects.items():
#             added_subjects[sub_id] = Subject(usos_id=sub_id,
#                     name=sub_val['name']
#                     )
#             added_subjects[sub_id].save()
#             print(added_subjects[sub_id])
#             print("=============")
#             print(set(sub_val['lecturers']))
#             for lec in set(sub_val['lecturers']):
#                 print(new_teachers[int(lec)])
#                 Class(teacher=new_teachers[int(lec)],
#                       subject=added_subjects[sub_id]
#                       ).save()
#             print("=============")
#
#         for comment in new_comments:
#             TeacherComment(teacher=new_teachers[int(comment['teacher'])],
#                            subject=added_subjects[comment['subject']],
#                            content=comment['content'],
#                            add_date=comment['add_date'],
#                            wikispaces=comment['wikispaces'],
#                            up_votes=comment['up_votes'],
#                            down_votes=comment['down_votes'],
#                            visible=comment['visible']
#                            ).save()
#
#         print(mapping)
#         print(new_subjects)
#         print(new_comment)
#         print(usos_teachers)




