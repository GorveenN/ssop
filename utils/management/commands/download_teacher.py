import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from app.models import Teacher

base_url = 'https://www.mimuw.edu.pl/osoba/'

class TooManyTags(Exception):
    pass

def find_only(soup, class_name):
    res = soup(class_=class_name)
    if len(res) > 1:
        raise TooManyTags(class_name)
    return res[0]

def download_teacher_info(usos_id):
    """ Connect to mimuw.edu.pl and download data about teacher with given usos_id.
        Return list [forename, surname, site, mail] or None, if teacher does not exist.
    """
    req = requests.get(base_url + str(usos_id))
    if req.status_code == 404:
        return None
    soup = BeautifulSoup(req.text, 'html.parser').find(id='block-system-main')

    name = find_only(soup, 'nazwisko').get_text().strip()
    surname = name.split(' ')[-1]
    forename = name.rstrip(surname).strip()

    """ Change html list of information to dictionary. """
    raw_info = find_only(soup, 'pracownik-description dontsplit').find_all('li')
    dict_info = {}
    for info in raw_info:
        key = find_only(info, 'nazwa').get_text().strip().replace(':', '')
        value = find_only(info, 'opis').get_text().strip()
        dict_info[key] = value

    site = dict_info['Strona www']
    mail = dict_info['E-mail']

    return [forename, surname, site, mail]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('usos_id', nargs='*', type=int)

    def handle(self, *args, **options):
        if options['usos_id']:
            for id in options['usos_id']:
                print(download_teacher_info(id))
        else:
            for t in Teacher.objects.all():
                r = download_teacher_info(t.usos_id)
                print(str(t.usos_id) + " " + str(r))
                if r is not None:
                    if r[2] and r[2] != '':
                        t.website = r[2]
                    if r[3] and r[3] != '':
                        t.email = r[3]
                    t.save()
