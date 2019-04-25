from django.core.management.base import BaseCommand
from retrying import retry
import requests
import json

# Execute query until it doesn't throw exception.
@retry
def try_query(string):
    return requests.get(string)


def get_subject_teacher(subject_id, editions):

    query = "https://usosapps.uw.edu.pl/services/courses/course_edition?course_id={}&term_id={}&fields=lecturers"
    lecturers = {}


    for edition in editions:
        # print("Checking edition: " + edition)
        response = try_query(query.format(subject_id, edition)).json()
        if 'message' not in response and response['lecturers']:
            for lecturer in response['lecturers']:
                lecturers[int(lecturer['user_id'])] = {
                    "firstname": lecturer['first_name'],
                    "surname": lecturer['last_name'],
                    "website": None,
                    "email": None
                }
    return lecturers


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Fetch usos data.'

        parser.add_argument('--editions',
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
            editions = {'2018', '2018L', '2018Z',
                        '2017', '2017L', '2017Z',
                        '2016', '2016L', '2016Z',
                        '2015', '2015L', '2015Z',
                        '2014', '2014L', '2014Z',
                        '2013', '2013L', '2013Z',
                        }

        query1 = "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name&name={}"
        query2 = "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name&name={}{}"
        query3 = "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name|is_currently_conducted&name={}{}{}&num=20&start={}"
        subjects = dict()
        visited_ids = set()
        # Must add ommiting already added courses in case of course repetition.
        for letter1 in alphabet:
            if try_query(query1.format(letter1)).json()['items']:
                for letter2 in alphabet:
                    if try_query(query2.format(letter1, letter2)).json()['items']:
                        for letter3 in alphabet:
                            print("======================")
                            print('Searching for phrase: ' + letter1 + letter2 + letter3)
                            print("======================")
                            response = {'items': [], 'next_page': True}
                            i = 0
                            while response['next_page']:
                                response = try_query(query3.format(letter1, letter2, letter3, i)).json()
                                for subject in response['items']:
                                    if subject['id'] not in visited_ids and subject['id'][:4] == '1000' and subject['is_currently_conducted']:
                                        visited_ids.add(subject['id'])
                                        print('------: ' + subject['name']['pl'])
                                        lecturers = get_subject_teacher(subject['id'], editions)
                                        if len(lecturers):
                                            subjects[subject['id']] = {
                                                "name": subject['name']['pl'],
                                                "lecturers": lecturers
                                            }
                                            print("Added course entry.")
                                        else:
                                            print("Course seems to be inactive.")
                                i += 20


        # query1 = "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name&name={}"
        # query2 = "https://usosapps.uw.edu.pl/services/courses/search?lang=pl&fac_id=10000000&fields=id|name|is_currently_conducted&name={}{}&num=20&start={}"
        # subjects = dict()
        #
        # for letter1 in alphabet:
        #     if try_query(query1.format(letter1)).json()['items']:
        #         for letter2 in alphabet:
        #                     print("======================")
        #                     print('Searching for phrase: ' + letter1 + letter2)
        #                     print("======================")
        #                     response = {'items': [], 'next_page': True}
        #                     i = 0
        #                     while response['next_page']:
        #                         response = try_query(query2.format(letter1, letter2, i)).json()
        #                         for subject in response['items']:
        #                             if subject['id'][:4] == '1000' and subject['is_currently_conducted']:
        #                                 print(subject['name']['pl'])
        #                                 lecturers = get_subject_teacher(subject['id'], editions)
        #                                 if len(lecturers):
        #                                     subjects[subject['id']] = {
        #                                         "name": subject['name']['pl'],
        #                                         "lecturers": lecturers
        #                                     }
        #                                     print("Added course entry.")
        #                                 else:
        #                                     print("Course seems to be inactive.")
        #                         i += 20
        #
        json.dump(subjects, open(options['output'], 'w'), indent=4)


# example output

# {
#     "1000-2N09ZSO": {
#         "name": "Zaawansowane systemy operacyjne",
#         "lecturers": {
#             "397": {
#                 "firstname": "Janina",
#                 "surname": "Mincer-Daszkiewicz",
#                 "website": null,
#                 "email": null
#             }
#         }
#     }
# }

# services/courses/course_edition example response
# {
#     "lecturers": [
#         {
#             "last_name": "Janowska",
#             "first_name": "Agata",
#             "id": "325",
#             "user_id": "325"
#         }
#     ]
# }

# services/courses/search example response
#
# {
#     "items": [
#         {
#             "id": "1000-1M00BO",
#             "name": {
#                 "pl": "Badania operacyjne",
#                 "en": "Operation research"
#             }
#         }
#     ],
#     "next_page": true
# }