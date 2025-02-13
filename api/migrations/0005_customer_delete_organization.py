# Generated by Django 5.1.5 on 2025-02-10 15:27

import cr.inve_lib.inve_lib
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_organization_address_alter_organization_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias_id', models.TextField(default=cr.inve_lib.inve_lib.generate_alias_id, editable=False, max_length=10, unique=True)),
                ('name', models.TextField()),
                ('is_parent', models.BooleanField(default=False)),
                ('address', models.TextField(blank=True, null=True)),
                ('phone', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='api.customer')),
            ],
        ),
        migrations.DeleteModel(
            name='Organization',
        ),
    ]
