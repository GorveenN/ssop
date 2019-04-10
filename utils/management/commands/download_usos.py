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
                        print(letter1 + letter2 + letter3)
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
        print(subject['name']['pl'])
        added = False
        for edition in editions:
            print(edition)
            response = requests.get(
                "https://usosapps.uw.edu.pl/services/courses/course_edition?course_id={}&term_id={}&fields=lecturers".format(subject['id'], edition)).json()
            print(response)
            if 'message' not in response and response['lecturers']:
                added = True
                subject[edition] = [response['lecturers']]
        if added:
            filtered += [subject]
            print("--- added course entry ---")
        else:
            print("--- course seems to be inactive ---")
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


def format_usos_data(editions, alphabet):
    return get_recent(editions, filter_active_courses(fetch_usos_subj(alphabet), editions))


# Filters wikispaces data to get only subjects with given model.
def filter_data_by_model(jason, model):
    empty = []
    for item in jason:
        if item['model'] == model:
            empty += [item]
    return empty

# alphabet = '123456789aąbcćdeęfghijklłmnńoóprsśtuwyzźż'
# entries = {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z',
#            '2012L', '2012Z', '2011L', '2011Z', '2010L', '2010Z'}
#
# print(format_usos_data(entries, alphabet))


# ===================================================== #
#                       Mapping
# ===================================================== #

# Returns teachers list who taught given subjects in db compliant form.
def filter_teachers(editions, subjects):
    empty = []
    for subject in subjects:
        for edition in editions:
            if edition in subject:
                for lec in subject[edition][0]:
                    add = dict()
                    add['model'] = 'app.teacher'
                    add['pk'] = lec['id']
                    add['fields'] = dict()
                    add['fields']['firstname'] = lec['first_name']
                    add['fields']['surname'] = lec['last_name']
                    add['fields']['website'] = None
                    add['fields']['email'] = None

                    empty += [add]

    new = {item['pk']: item for item in empty}
    return [new[item] for item in new]

# jason = filter_teachers(
#     {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z'},
#     json.load(open('usos.json')))


# Return map where subject from wikispaces is mapped to all possible subjects from usos.
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


# Creates map template.
def create_mapping_template(wikispaces_data):
    dump = filter_data_by_model(wikispaces_data, "app.subject")
    empty = []

    for item in dump:
        to_add = dict()
        to_add['from'] = item['pk']
        to_add['name'] = item['fields']['name']
        to_add['to'] = None
        empty += [to_add]
    return dump

# usos_data = json.load(open('subjects_from_5_years.json'))
# wikispaces_data = json.load(open('../fixtures/app.json'))
# map_subject_old_new(wikispaces_data, usos_data)

# ===================================================== #
#                       Mapping ends :)
# ===================================================== #


# entries = {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z',
#            '2012L', '2012Z', '2011L', '2011Z', '2010L', '2010Z'}
#
# jason = get_recent(
#     {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z'},
#     json.load(open('usos.json')))
#
# json.dump(get_current_courses(json.load(open('app.json'))))