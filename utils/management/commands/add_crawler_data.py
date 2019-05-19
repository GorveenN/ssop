from django.core.management.base import BaseCommand
from app.models import *
import json


def load_json(filename):
    return json.load(open(filename))


def save_json(jason, filename):
    json.dump(jason, open(filename, 'w'), indent=4)


def fill_db(table, data):
    for item in data:
        table(name=item).save()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Add usosweb data.'
        parser.add_argument('--data', type=str)

    def handle(self, *args, **options):
        usos_json = load_json(options['data'])

        language_set = set()
        period_set = set()
        type_of_course_set = set()
        groups_of_courses_set = set()
        types_of_classes_set = set()

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

            language = value['language']
            if language != '(brak danych)' and language != '':
                language_set.add(language)
                db_obj.language = language

            period = value['period']
            if period != '(brak danych)' and period != '':
                period_set.add(period)
                db_obj.period = value['period']

            type_of_course = value['type_of_course']
            if type_of_course != '(brak danych)' and type_of_course != '':
                type_of_course_set.add(type_of_course)
                db_obj.type_of_course = value['type_of_course']

            groups_of_courses = value['groups']
            for item in groups_of_courses:
                if item != '':
                    groups_of_courses_set.add(item)
            db_obj.groups_of_courses = value['groups']

            types_of_classes = []
            for type in value['types_of_classes']:
                type_of_class = type.split(',')[0]
                types_of_classes_set.add(type_of_class)
                types_of_classes += [type_of_class]
            db_obj.types_of_classes = types_of_classes

            db_obj.save()

        fill_db(CourseLanguage, language_set)
        fill_db(CoursePeriod, period_set)
        fill_db(CourseType, type_of_course_set)
        fill_db(CourseGroup, groups_of_courses_set)
        fill_db(ClassType, types_of_classes_set)
