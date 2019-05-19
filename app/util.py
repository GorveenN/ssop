import json


def escape_string(s):
    return json.dumps(s).replace('"', '')


def make_choices(objects):
    choices = ()
    for item in objects:
        choices += ((item.name, item.name),)
    return choices


def ects_choices():
    tup = ()
    for i in range(0, 21):
        tup += ((i, i),)
    return tup
