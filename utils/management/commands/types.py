from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--courses', type=str)

    def handle(self, *args, **options):
        jason = json.load(open(options['courses']))
        # print(jason)
        type_of_courses = set()
        type_of_classes = set()
        period = set()
        groups = set()
        for key, value in jason.items():
            type_of_courses.add(value['type_of_course'])
            for type_of_class in value['types_of_classes']:
                type_of_classes.add(type_of_class.split(',')[0])
            period.add(value['period'])
            for group in value['groups']:
                groups.add(group)

        print("types of courses:")
        print(type_of_courses)
        print("types of classes:")
        print(type_of_classes)
        print("period:")
        print(period)
        print("groups:")
        print(groups)



