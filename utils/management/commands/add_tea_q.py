from django.core.management.base import BaseCommand
from app.models import *
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--jason', type=str)

    def handle(self, *args, **options):
        jason = json.load(open(options['jason']))
        for item in jason:
            print(item)
            TeacherSurveyQuestion(question_text=item['question_text']).save()