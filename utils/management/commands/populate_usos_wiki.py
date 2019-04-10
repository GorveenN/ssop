from django.core.management.base import BaseCommand
#from app.models import Teacher
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
        # usos_subjects = load_json(options['usos_subjects'])
        usos_teachers = load_json(options['usos_teachers'])
        # wikispaces_data = load_json(options['wikispaces'])
        # map = load_json(options['map'])

        _classes = {}

        new_teachers = {}
        new_comments = []

        print(usos_teachers)

        for teacher in usos_teachers:
            Teacher(firstname=teacher['fields']['firstname'], surname=teacher['fields']['surname'],
                    usos_id=int(teacher['pk']), website=None, email=None
                    ).save()
