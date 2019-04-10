from django.core.management.base import BaseCommand
import requests
import json


def load_json(filename):
    return json.load(open(filename))


def save_json(jason, filename):
    json.dump(jason, open(filename, 'w'), indent=4)


# Returns possibly all courses taught at MIMUW faculty.
def fetch_usos_subj(alphabet):
    subjects = []
    for letter1 in alphabet:
        if requests.get(
                "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name&name={}".format(
                    letter1)).json()['items']:
            for letter2 in alphabet:
                if requests.get(
                        "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name&name={}{}".format(
                            letter1, letter2)).json()['items']:
                    for letter3 in alphabet:
                        print('Searching for phrase: ' + letter1 + letter2 + letter3)
                        response = {'items': [], 'next_page': True}
                        i = 0
                        while response['next_page']:
                            response = requests.get(
                                "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name|is_currently_conducted|profile_url&name={}{}{}&num=20&start={}".format(
                                    letter1, letter2, letter3, i)).json()
                            for subject in response['items']:
                                if subject['id'][:4] == '1000' and subject['is_currently_conducted']:
                                    subjects += [subject]
                            i += 20
    return subjects


# Returns list of subjects with data about its editions(list of teachers).
def filter_active_courses(subjects, editions):
    filtered = []
    for subject in subjects:
        print('==============================')
        print(subject['name']['pl'])
        added = False
        for edition in editions:
            print("Checking edition: " + edition)
            response = requests.get(
                "https://usosapps.uw.edu.pl/services/courses/course_edition?course_id={}&term_id={}&fields=lecturers".format(subject['id'], edition)).json()
            if 'message' not in response and response['lecturers']:
                added = True
                subject[edition] = [response['lecturers']]
        if added:
            filtered += [subject]
            print("Added course entry.")
        else:
            print("Course seems to be inactive.")
    return filtered


# Returns subjects list with list of teachers who taught given subject.
def get_recent(editions, courses):
    empty = []
    for item in courses:
        new_item = dict()
        new_item['id'] = item['id']
        new_item['url'] = item['profile_url']
        new_item['name'] = item['name']['pl']
        new_item['lecturers'] = []
        for edition in editions:
            if edition in item:
                for lecturer in item[edition][0]:
                    new_item['lecturers'] += [lecturer['id']]
        if new_item['lecturers']:
            new_item['lecturers'] = list(dict.fromkeys(new_item['lecturers']))
            empty += [new_item]
    return empty


# Returns teachers list who taught given subjects in db compliant form.
# It takes as argument raw usos output.
def filter_teachers(editions, subjects):
    empty = {}
    for subject in subjects:
        for edition in editions:
            if edition in subject:
                for lec in subject[edition][0]:
                    lec_id = lec['id']
                    empty[lec_id] = dict()
                    empty[lec_id]['firstname'] = lec['first_name']
                    empty[lec_id]['surname'] = lec['last_name']
                    empty[lec_id]['website'] = None
                    empty[lec_id]['email'] = None
    return empty


# ===================================================== #
#                       Mapping
# ===================================================== #

# Return map where subject from wikispaces is mapped to all possible subjects from usos.
# wikispaces_data is old db dump where usos_data is formated usos data.
def map_subject_old_new(wikispaces_data, usos_data):
    teacher_to_subject = dict()

    for subject in usos_data:
        for teacher in subject['lecturers']:
            teacher_id = int(teacher)
            if teacher not in teacher_to_subject:
                teacher_to_subject[teacher_id] = dict()
            teacher_to_subject[teacher_id][subject['id']] = subject['name']

    print(teacher_to_subject)

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
    print(empty)

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
    json.dump(final_json, open('possible_mapping.json', 'w'), indent=4)


# usos_data = json.load(open('subjects_from_5_years.json'))
# wikispaces_data = json.load(open('../fixtures/app.json'))
# map_subject_old_new(wikispaces_data, usos_data)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Fetch usos data.'

        parser.add_argument('editions',
                            nargs='+',
                            type=str
                            )

        parser.add_argument('--alphabet',
                            type=str,
                            help='String used to search for subjects. '
                                 'Script will use every combination of 3 letters from this string as query argument.'
                            )

        parser.add_argument('--output',
                            type=str,
                            help='Specifies path where json will be saved.')


    def handle(self, *args, **options):
        if options['alphabet']:
            alphabet = options['alphabet']
        else:
            alphabet = '123456789aąbcćdeęfghijklłmnńoóprsśtuwyzźż'

        if options['editions']:
            editions = options['editions']
        else:
            editions = {'2018L', '2018Z',
                        '2017L', '2017Z',
                        '2016L', '2016Z',
                        '2015L', '2015Z',
                        '2014L', '2014Z',
                        '2013L', '2013Z',
                        '2012L', '2012Z',
                        '2011L', '2011Z',
                        '2010L', '2010Z'
                        }

        usos_dump = fetch_usos_subj(alphabet)
        save_json(get_recent(editions, filter_active_courses(usos_dump, editions)), 'subjects_' + options['output'])
        save_json(filter_teachers(editions, usos_dump), 'teachers_' + options['output'])

