# Generated by Django 2.0.3 on 2019-05-19 10:53

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Class',
                'verbose_name_plural': 'Classes',
            },
        ),
        migrations.CreateModel(
            name='ClassType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CoursePeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('done', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('usos_id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('ects', models.FloatField(default=None, null=True)),
                ('language', models.CharField(default=None, max_length=32, null=True)),
                ('period', models.CharField(default=None, max_length=32, null=True)),
                ('type_of_course', models.CharField(default=None, max_length=32, null=True)),
                ('groups_of_courses', jsonfield.fields.JSONField(default=None, null=True)),
                ('types_of_classes', jsonfield.fields.JSONField(default=None, null=True)),
            ],
            options={
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
            },
        ),
        migrations.CreateModel(
            name='SubjectComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('up_votes', models.IntegerField(default=0)),
                ('down_votes', models.IntegerField(default=0)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Subject')),
            ],
            options={
                'verbose_name': 'Subject comment',
                'verbose_name_plural': 'Subject comments',
            },
        ),
        migrations.CreateModel(
            name='SubjectSurveyAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Subject survey answer',
                'verbose_name_plural': 'Subject survey answer',
            },
        ),
        migrations.CreateModel(
            name='SubjectSurveyQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Subject survey question',
                'verbose_name_plural': 'Subject survey questions',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('firstname', models.CharField(max_length=64)),
                ('surname', models.CharField(max_length=64)),
                ('usos_id', models.IntegerField(primary_key=True, serialize=False)),
                ('website', models.CharField(max_length=64, null=True)),
                ('email', models.CharField(max_length=64, null=True)),
            ],
            options={
                'verbose_name': 'Teacher',
                'verbose_name_plural': 'Teachers',
                'ordering': ['surname'],
            },
        ),
        migrations.CreateModel(
            name='TeacherComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('wikispaces', models.BooleanField(default=False)),
                ('up_votes', models.IntegerField(default=0)),
                ('down_votes', models.IntegerField(default=0)),
                ('visible', models.BooleanField(default=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Subject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Teacher')),
            ],
            options={
                'verbose_name': 'Teacher comment',
                'verbose_name_plural': 'Teacher comments',
            },
        ),
        migrations.CreateModel(
            name='TeacherSurveyAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Teacher survey answer',
                'verbose_name_plural': 'Teacher survey answer',
            },
        ),
        migrations.CreateModel(
            name='TeacherSurveyQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Teacher  survey question',
                'verbose_name_plural': 'Teacher survey questions',
            },
        ),
        migrations.AddField(
            model_name='teachersurveyanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.TeacherSurveyQuestion'),
        ),
        migrations.AddField(
            model_name='teachersurveyanswer',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Subject'),
        ),
        migrations.AddField(
            model_name='teachersurveyanswer',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Teacher'),
        ),
        migrations.AddField(
            model_name='subjectsurveyanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.SubjectSurveyQuestion'),
        ),
        migrations.AddField(
            model_name='subjectsurveyanswer',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Subject'),
        ),
        migrations.AddField(
            model_name='report',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.TeacherComment'),
        ),
        migrations.AddField(
            model_name='class',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Subject'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Teacher'),
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('teacher', 'subject')},
        ),
    ]
