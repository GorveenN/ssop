from django.core.management.base import BaseCommand
import json


def load_json(filename):
    return json.load(open(filename))


def save_json(jason, filename):
    json.dump(jason, open(filename, 'w'), indent=4)

# Return map where subject from wikispaces is mapped to all possible subjects from usos.
# wikispaces_data is old db dump where usos_data is formated usos data.
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Creates mapping from wikispaces to usos data.'

        parser.add_argument('--wikispaces',
                            type=str,
                            help='Specifies path to wikispaces data.'
                            )

        parser.add_argument('--usos',
                            type=str,
                            help='Specifies path to usos data.'
                            )

        parser.add_argument('--output',
                            type=str,
                            help='Specifies path to file where mapping will be saved.'
                            )

    def handle(self, *args, **options):
        usos_data = load_json(options['usos'])
        wikispaces_data = load_json(options['wikispaces'])
        teacher_to_subject = dict()

        for subject in usos_data:
            for teacher in subject['lecturers']:
                teacher_id = int(teacher)
                if teacher not in teacher_to_subject:
                    teacher_to_subject[teacher_id] = dict()
                teacher_to_subject[teacher_id][subject['id']] = subject['name']

        empty = dict()
        for comment in wikispaces_data:
            if comment['model'] == "app.teachercomment":
                sub_id = comment['fields']['subject_exact']
                teach_id = comment['fields']['teacher']
                if sub_id not in empty:
                    empty[sub_id] = dict()
                if teach_id in teacher_to_subject:
                    for key, value in teacher_to_subject[teach_id].items():
                        empty[sub_id][key] = value

        final_json = []
        for item in wikispaces_data:
            if item['model'] == "app.subject":
                to_add = dict()
                to_add['from'] = item['pk']
                to_add['name'] = item['fields']['name']
                to_add['to'] = None
                if item['pk'] not in empty:
                    empty[item['pk']] = dict()
                to_add['poss'] = empty[item['pk']]
                final_json += [to_add]
        json.dump(final_json, open(options['output'], 'w'), indent=4)

