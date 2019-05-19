from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata
from django.core import management


class Command(BaseCommand):
    def handle(self, *args, **options):
        management.call_command('populate_usos_wiki',
                                map='fixtures/map.json',
                                usos='fixtures/usos.json',
                                wiki='fixtures/wiki.json')

        management.call_command('add_sub_q',
                                jason='fixtures/subject_surveys.json')

        management.call_command('add_tea_q',
                                jason='fixtures/teacher_surveys.json')
        management.call_command('add_crawler_data',
                                data='fixtures/courses.json')




