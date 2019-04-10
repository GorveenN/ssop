from app.models import Teacher

t = Teacher(firstname='test', surname='testowski', usos_id=2)
t.save()

# firstname = models.CharField(max_length=64)
# surname = models.CharField(max_length=64)
# usos_id = models.IntegerField(primary_key=True)
# website = models.CharField(max_length=64, null=True)
# email = models.CharField(max_length=64, null=True)