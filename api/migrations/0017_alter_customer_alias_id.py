# Generated by Django 5.1.5 on 2025-02-23 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_customer_branch_alter_chequestore_alias_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='alias_id',
            field=models.TextField(default='2243cbff34', editable=False, max_length=10, unique=True),
        ),
    ]
