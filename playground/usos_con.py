import requests
import json


def fetch_usos_subj(dict):
    empty = []
    for letter1 in dict:
        if requests.get(
                "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name&name={}".format(
                    letter1)).json()['items']:
            for letter2 in dict:
                if requests.get(
                        "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name&name={}{}".format(
                            letter1, letter2)).json()['items']:
                    for letter3 in dict:
                        print(letter1 + letter2 + letter3)
                        response = {'items': [], 'next_page': True}
                        i = 0
                        while response['next_page']:
                            response = requests.get(
                                "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name|is_currently_conducted|profile_url&name={}{}{}&num=20&start={}".format(
                                    letter1, letter2, letter3, i)).json()
                            for entry in response['items']:
                                if entry['id'][:4] == '1000' and entry['is_currently_conducted']:
                                    empty += [entry]
                            i += 20
    return empty


def remove_mult(jason):
    unique = {each['id']: each for each in jason}
    unique2 = [unique[item] for item in unique]
    print(unique2)
    return unique2


def filter_active_courses(jason, entries):
    after_filter = []
    for item in jason:
        print(item['name']['pl'])
        added = False
        for entry in entries:
            response = requests.get(
                "https://usosapps.uw.edu.pl/services/courses/course_edition?course_id={}&term_id={}&fields=lecturers".format(
                    item['id'], entry)).json()
            if 'message' not in response and response['lecturers']:
                added = True
                item[entry] = [response['lecturers']]
        if added:
            after_filter += [item]
            print("--- added course entry ---")
        else:
            print("--- course seems to be inactive ---")
    return after_filter


alphabet = '123456789aąbcćdeęfghijklłmnńoóprsśtuwyzźż'
entries = {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z',
           '2012L', '2012Z', '2011L', '2011Z', '2010L', '2010Z'}


# Returns subject list with teachers filtered by subject edition.
def get_recent(entries, jason):
    empty = []
    for item in jason:
        new_item = dict()
        new_item['id'] = item['id']
        new_item['url'] = item['profile_url']
        new_item['name'] = item['name']['pl']
        new_item['lecturers'] = []
        for entry in entries:
            if entry in item:
                for lec in item[entry][0]:
                    new_item['lecturers'] += [lec['id']]
        if new_item['lecturers']:
            new_item['lecturers'] = list(dict.fromkeys(new_item['lecturers']))
            empty += [new_item]
    print(json.dumps(empty, indent=2))
    return empty


# Filters app_data to get only subjects entries.
def get_current_courses(jason):
    empty = []
    for item in jason:
        if item['model'] == 'app.subject':
            empty += [item]
    return empty


entries = {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z',
           '2012L', '2012Z', '2011L', '2011Z', '2010L', '2010Z'}

jason = get_recent(
    {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z'},
    json.load(open('usos_dump.json')))

json.dump(get_current_courses(json.load(open('app.json'))))