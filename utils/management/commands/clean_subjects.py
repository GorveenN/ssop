from app.models import *
from django.core.management.base import BaseCommand

NAMES = ['Wszystko co się da',
         'Ogólnie:',
         'Ogólne uwagi',
         'Uwagi ogólne:',
         'Uwagi Ogólne',
         'Uwagi ogolne',
         'Ogólnie',
         'Uwagi ogólne',
         'Pan Plaskota to...',
         'Uwagi z boku',
         'Wrażenie ogólne',
         'Dyskusje Ogólne',
         'Uwagi ogolne:'
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        subjectOgolne = Subject.objects.get(name='Ogólne')
        ogolneExact = SubjectExact.objects.get(subject=subjectOgolne)

        for i in NAMES:
            try:
                sub = Subject.objects.get(name=i)
                for sube in sub.subjectexact_set.all():
                    sube.teachercomment_set.all().update(subject_exact=ogolneExact)
                    sube.class_set.all().update(subject_exact=ogolneExact)
                sub.delete()
            except Subject.DoesNotExist:
                pass

