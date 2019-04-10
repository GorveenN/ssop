from data_processing import data_manipulation as man


# ZPP issue
alphabet = 'zes'
entries = {'2018L', '2018Z', '2017L', '2017Z', '2016L', '2016Z', '2015L', '2015Z', '2014L', '2014Z', '2013L', '2013Z'}
#man.save_json(man.format_usos_data(entries, alphabet), 'zpp.json')

#man.filter_active_courses(man.fetch_usos_subj(alphabet), entries)


from app.models import Teacher

t = Teacher(firstname='test', surname='testowski', usos_id=2)
t.save()

# firstname = models.CharField(max_length=64)
# surname = models.CharField(max_length=64)
# usos_id = models.IntegerField(primary_key=True)
# website = models.CharField(max_length=64, null=True)
# email = models.CharField(max_length=64, null=True)