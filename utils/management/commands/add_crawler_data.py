from django.core.management.base import BaseCommand
from app.models import *
import json


def load_json(filename):
    return json.load(open(filename))


def save_json(jason, filename):
    json.dump(jason, open(filename, 'w'), indent=4)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Add usosweb data.'
        parser.add_argument('--data', type=str)

    def handle(self, *args, **options):
        usos_json = load_json(options['data'])

        for key, value in usos_json.items():
            print(key)

            try:
                db_obj = Subject.objects.get(usos_id=key)
            except Subject.DoesNotExist:
                continue

            try:
                db_obj.ects = float(value['ects'].split(' ')[0])
            except ValueError:
                db_obj.ects = None

            db_obj.language = value['language']
            db_obj.period = value['period']
            db_obj.type_of_course = value['type_of_course']
            db_obj.groups_of_courses = value['groups']
            types_of_classes = []
            for type in value['types_of_classes']:
                print(type.split(',')[0])
                types_of_classes += [type.split(',')[0]]
            db_obj.types_of_classes = types_of_classes
            db_obj.save()
