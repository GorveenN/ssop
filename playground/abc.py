import requests
import json


def filter_teachers(entries, jason):
    empty = []
    for item in jason:
        for entry in entries:
            if entry in item:
                for lec in item[entry][0]:
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
#     json.load(open('usos_dump.json')))
#
#
# # Creates map template.
# with open('../fixtures/app.json') as file:
#     dump = json.load(file)
#     empty = []
#
#     for item in dump:
#         if item['model'] == "app.teachercomment":
#             to_add = dict()
#             to_add['from'] = item['pk']
#             to_add['name'] = item['fields']['name']
#             to_add['to'] = None
#             empty += [to_add]
#     json.dump(empty, open('map.json', 'w'), indent=4)

    # "model": "app.teachercomment",
    # "pk": 635,
    # "fields": {
    #     "teacher": 319,
    #     "subject_exact": 138,
    #     "content": "Bardzo mi\u0142o wspomionam p.Janusza - student OEIIZK",
    #     "add_date": "2018-04-12T16:40:30.218Z",
    #     "wikispaces": true,
    #     "up_votes": 0,
    #     "down_votes": 0,
    #     "visible": true
    # }

    # {
    #     "id": "1000-111ADM1",
    #     "url": "https://usosweb.uw.edu.pl/kontroler.php?_action=katalog2/przedmioty/pokazPrzedmiot&prz_kod=1000-111ADM1",
    #     "name": "Algebra dla MSEM I",
    #     "lecturers": [
    #         "464",
    #         "279",
    #         "343",
    #         "62157"
    #     ]
    # # },


def map_subject_old_new(jason_old, usos_dump):
    teacher_to_subject = dict()

    for subject in usos_dump:
        for teacher in subject['lecturers']:
            teacher_id = int(teacher)
            if teacher not in teacher_to_subject:
                teacher_to_subject[teacher_id] = dict()
            teacher_to_subject[teacher_id][subject['id']] = subject['name']

    print(teacher_to_subject)

    empty = dict()
    for comment in jason_old:
        if comment['model'] == "app.teachercomment":
            sub_id = comment['fields']['subject_exact']
            teach_id = comment['fields']['teacher']
            if sub_id not in empty:
                empty[sub_id] = dict()
            if teach_id in teacher_to_subject:
                for key, value in teacher_to_subject[teach_id].items():
                    empty[sub_id][key] = value
    print(empty)

    final_json  = []
    for item in jason_old:
        if item['model'] == "app.subject":
            to_add = dict()
            to_add['from'] = item['pk']
            to_add['name'] = item['fields']['name']
            to_add['to'] = None
            if item['pk'] not in empty:
                empty[item['pk']] = dict()
            to_add['poss'] = empty[item['pk']]
            final_json += [to_add]
    json.dump(final_json, open('map2.json', 'w'), indent=4)


usos_data = json.load(open('5years.json'))
wikispaces_data = json.load(open('../fixtures/app.json'))

map_subject_old_new(wikispaces_data, usos_data)

