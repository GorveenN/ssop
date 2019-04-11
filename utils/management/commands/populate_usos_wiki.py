from django.core.management.base import BaseCommand
from app.models import *
import json


def load_json(filename):
    return json.load(open(filename))


def save_json(jason, filename):
    json.dump(jason, open(filename, 'w'), indent=4)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Fetch usos data.'

        parser.add_argument('--map',
                            type=str
                            )

        parser.add_argument('--usos_subjects',
                            type=str,
                            help='String used to search for subjects. '
                                 'Script will use every combination of 3 letters from this string as query argument.'
                            )

        parser.add_argument('--usos_teachers',
                            type=str,
                            help='Specifies path where json will be saved.')

        parser.add_argument('--wikispaces',
                            type=str,
                            help='Specifies path where json will be saved.')

    def handle(self, *args, **options):
        usos_subjects = load_json(options['usos_subjects'])
        usos_teachers = load_json(options['usos_teachers'])
        wikispaces_data = load_json(options['wikispaces'])
        map = load_json(options['map'])


        new_mapping = {}
        for subject in map:
            new_mapping[int(subject['from'])] = subject['to']

        new_subjects = {}
        for subject in usos_subjects:
            new_subjects[subject['id']] = dict()
            new_subjects[subject['id']]['name'] =  subject['name']
            new_subjects[subject['id']]['lecturers'] =  [int(x) for x in subject['lecturers']]
        print(new_subjects)

        new_comments = []
        print(new_mapping)
        new_teachers = {}
        for teacher in wikispaces_data:
            if teacher['model'] == "app.teacher":
                new_teachers[int(teacher['pk'])] = \
                    Teacher(firstname=teacher['fields']['firstname'],
                            surname=teacher['fields']['surname'],
                            usos_id=int(teacher['pk']),
                            website=teacher['fields']['website'],
                            email=teacher['fields']['email']
                            )
                new_teachers[int(teacher['pk'])].save()
            elif teacher['model'] == "app.teachercomment":
                new_comment = {}
                print(teacher['fields']['teacher'])
                print(new_mapping[int(teacher['fields']['subject_exact'])])
                new_subjects[new_mapping[int(teacher['fields']['subject_exact'])]]['lecturers'] += [teacher['fields']['teacher']]
                new_comment['teacher'] = teacher['fields']['teacher']
                new_comment['subject'] = new_mapping[int(teacher['fields']['subject_exact'])]
                new_comment['content'] = teacher['fields']['content']
                new_comment['add_date'] = teacher['fields']['add_date']
                new_comment['wikispaces'] = teacher['fields']['wikispaces']
                new_comment['up_votes'] = teacher['fields']['up_votes']
                new_comment['down_votes'] = teacher['fields']['down_votes']
                new_comment['visible'] = teacher['fields']['visible']
                new_comments += [new_comment]

        for teacher in usos_teachers:
            new_teachers[int(teacher['pk'])] = \
                Teacher(firstname=teacher['fields']['firstname'],
                    surname=teacher['fields']['surname'],
                    usos_id=int(teacher['pk']),
                    website=None, email=None
                    )
            new_teachers[int(teacher['pk'])].save()

        added_subjects = {}
        for sub_id, sub_val in new_subjects.items():
            t = Subject(usos_id=sub_id,
                    name=sub_val['name']
                    )
            t.save()
            added_subjects[sub_id] = t
            print(t)
            print("=============")
            print(set(sub_val['lecturers']))
            for lec in set(sub_val['lecturers']):
                print(new_teachers[int(lec)])
                Class(teacher=new_teachers[int(lec)],
                      subject=t
                      ).save()
            print("=============")

        print(new_mapping)
        print(new_subjects)
        print(new_comment)
        print(usos_teachers)






