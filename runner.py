from data_processing import data_manipulation as man

from app.models import Teacher

t = Teacher(firstname='test', surname='testowski', usos_id=2)
t.save()
