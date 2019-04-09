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


jason = filter_teachers(
    {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z'},
    json.load(open('usos_dump.json')))


# Creates map template.
with open('app.json') as file:
    dump = json.load(file)
    empty = []

    for item in dump:
        if item['model'] == "app.subject":
            to_add = dict()
            to_add['from'] = item['pk']
            to_add['name'] = item['fields']['name']
            to_add['to'] = None
            empty += [to_add]
    json.dump(empty, open('map.json', 'w'), indent=4)
