import django
import argparse
from django.core.management import call_command
from django.core.management.base import BaseCommand
from io import StringIO

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Populate database with different methods'

        parser.add_argument(
            'method',
            choices=['wikispaces'],
            help='method of population'
        )

    def handle(self, *args, **options):
        if options['method'] == 'wikispaces':
            out = StringIO()

            print('--- Running command: download_wikispaces ---')
            call_command('download_wikispaces', '--return', stdout=out)

            print('--- Running command: populate_wikispaces ---')
            call_command('populate_wikispaces', '--arg-input', out.getvalue())

