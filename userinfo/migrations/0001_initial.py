# Generated by Django 2.1.4 on 2018-12-30 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=200)),
                ('singer', models.CharField(max_length=200)),
                ('album', models.CharField(max_length=200)),
                ('duration', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'song',
            },
        ),
        migrations.CreateModel(
            name='Songlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listname', models.CharField(max_length=200)),
                ('isdelete', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'songlist',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uname', models.CharField(max_length=50)),
                ('upwd', models.CharField(max_length=200)),
                ('uemail', models.EmailField(max_length=254, null=True)),
                ('isdelete', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.AddField(
            model_name='songlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userinfo.User'),
        ),
        migrations.AddField(
            model_name='song',
            name='songlist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userinfo.Songlist'),
        ),
    ]
