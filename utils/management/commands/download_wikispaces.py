# coding=utf-8
# This script runs corectly only with Python2!
import json
import re
from pysimplesoap.client import SoapClient
from django.core.management.base import BaseCommand
import logging.config
logging.config.dictConfig({
    'version': 1,
    # Other configs ...
    'disable_existing_loggers': True
})

class Comment(object):
    def __init__(self, przedmiot_nazwa, tresc):
        self.przedmiot_nazwa = przedmiot_nazwa
        self.tresc = tresc

class Person(object):
    def __init__(self, imie, nazwisko):
        self.imie = imie
        self.nazwisko = nazwisko
        self.komentarze = []

def get_teacher_names(arg):
    """
    Tries to extract surname and name.
    It covers three cases of fullname format e.g.
        - Nguyen, Hung Son
        - Wojciechowski Krszystof
        - Stępień-Baran,Agnieszka

    :param arg: string to parse
    :return: [surname, name] or None if fail
    """
    exceptions = ['Sekcja', 'Egz.']

    m = re.match('(?P<surname>[^, ]*)(?:,|, | )(?P<name>[^,]*)$', arg)
    if m and m.group('surname') not in exceptions:
        return [m.group('surname'), m.group('name')]
    else:
        return None

def get_usos_id(usos_link):
    m = re.search('os_id:(?P<id>[0-9]+)', usos_link)
    if m:
        return int(m.group('id'))
    else:
        return None

def save_to_file(obj, filename):
    with open(filename, 'w+', encoding='utf-8') as f:
        f.write(
            json.dumps(
                obj,
                default=lambda x: x.__dict__,
                indent=4,
                ensure_ascii=False
            )
        )

def clean_subject_name(subject_name_dirty):
    """Cut out all html tags and leading or trailing whitespaces"""
    subject_name = re.sub('<[^>]+>', '', subject_name_dirty).strip()

    """ **Analiza 1.2*** -> Analiza 1.2*  """
    subject_name = re.sub('\*\*', '', subject_name)

    return subject_name

def comments_from_page(page, debug):
    res = []
    sections = split_into_subject_sections(page)
    for subject_list in sections:
        if len(subject_list) != 2 or subject_list[0].isspace() or subject_list[1].isspace():
            continue
        if not subject_list[0] or not subject_list[1]:
            continue

        subject_content = subject_list[1]
        subject_name = clean_subject_name(subject_list[0])
        if debug:
            print("    " + subject_name)

        subject_comments = re.split(r'\n\*|^\*', subject_content)
        for comment in subject_comments:
            if not comment or comment.isspace() or comment == '[[toc]]':
                continue
            comment = comment.strip()
            res.append(Comment(subject_name, comment))
    return res

def split_into_subject_sections(arg):
    """
    Split arg into sections about one subject, using regex to find headings.
    :param arg: string to split
    :return: list of list with content regarding one subject.
    Each sublist is in the form ['title', 'content']
    """
    start = ['^', '\n']
    end = [r'\s*\n']
    header_start = [r'\*\*', '=']
    header_more = ['[=]*']
    header_start_reg = ''
    header_end_reg = ''
    for s in start:
        for h in header_start:
            for m in header_more:
                if header_start_reg != '':
                    header_start_reg += '|'
                header_start_reg += s + h + m

    for e in end:
        for h in header_start:
            for m in header_more:
                if header_end_reg != '':
                    header_end_reg += '|'
                header_end_reg += m + h + e

    m = re.split(header_start_reg, arg)
    res = []
    for section in m:
        res.append(re.split(header_end_reg, section))
    return res

def process_menu_item(menu_item):
    """
    Tries to parse menu_item.
    If succesfully retrives name, surname, and usos_id,
    then fills teachers dictionary and wikispaces_names dictionary.
    :param menu_item: string from wikispaces menu
    """
    m = re.match(r'\[\[(?P<names>[^\]]*)\]\] \[\[(?P<usos_link>[^\]]*)\]\]$', menu_item)
    if not m:
        return

    wiki_names = m.group('names').split('|')[0]
    name_list = get_teacher_names(m.group('names').split('|')[-1])
    if not name_list:
        return
    surname = name_list[0].strip()
    name = name_list[1].strip()
    usos_id = get_usos_id(m.group('usos_link'))
    if not usos_id:
        return

    return usos_id, Person(name, surname), wiki_names

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.help = 'Download data from mimuw.wikispaces.com'
        parser.add_argument(
            '-n',
            '--no-comments',
            action='store_true',
            help='saves an additional JSON without comments'
        )
        parser.add_argument(
            '-r',
            '--return',
            action='store_true',
            help='returns a result instead of saving it to file'
        )
        parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            help='debug mode'
        )

    def handle(self, *args, **options):
        print('Downloading data from: mimuw.wikispaces.com')

        print('Connecting to site API...', end='', flush=True)
        site_api = SoapClient(wsdl='https://mimuw.wikispaces.com/site/api?wsdl')
        print('done')

        print('Connecting to space API...', end='', flush=True)
        space_api = SoapClient(wsdl='https://mimuw.wikispaces.com/space/api?wsdl')
        print('done')

        print('Connecting to page API...', end='', flush=True)
        page_api = SoapClient(wsdl='https://mimuw.wikispaces.com/page/api?wsdl')
        print('done')

        print('All connections established...')

        username, password = 'io_crawler', 'io_crawler_wk'

        print('Logging to site API...', end='', flush=True)
        session = site_api.login(username=username, password=password)['return']
        print(f'done (session: {session})')

        print('Getting space id...', end='', flush=True)
        # TODO: Response isn't parsed
        # space = space_api.getSpace(session=session, name='mimuw')
        space_id = 33031
        print(f'done (space id: {space_id})')

        print('Getting menu site...', end='', flush=True)
        page = page_api.getPage(session=session, spaceId=space_id, name='space.menu')
        print('done')

        teachers = {}
        wikispaces_names = {}

        print('Downloading and parsing whole data (it may takes a while)...')
        """Get teacher's data (fullname and usos_id)"""
        for menu_item in page['page']['content'].split('\n'):
            ret = process_menu_item(menu_item)
            if ret:
                usos_id, person, wiki_names = ret
                teachers[usos_id] = person
                wikispaces_names[usos_id] = wiki_names

        if options['no_comments']:
            save_to_file(teachers, "wikispaces_no_comments.json")

        """Get comments from teacher's pages"""
        for id in teachers:
            wiki_name = wikispaces_names[id]
            if options['debug']:
                print(wiki_name + " " + str(id))
            page = page_api.getPage(session=session, spaceId=space_id, name=wiki_name)['page']['content']
            if page:
                teachers[id].komentarze = comments_from_page(page, debug=options['debug'])

        if options['return']:
            return json.dumps(
                teachers,
                default=lambda x: x.__dict__,
                indent=4,
                ensure_ascii=False
            )

        else:
            save_to_file(teachers, "wikispaces.json")
