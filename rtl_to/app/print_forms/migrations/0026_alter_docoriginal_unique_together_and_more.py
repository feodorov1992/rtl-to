# Generated by Django 4.1.13 on 2024-03-18 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0133_alter_extorder_currency_and_more'),
        ('print_forms', '0025_docoriginal_created_at_docoriginal_last_update_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='docoriginal',
            unique_together={('transit', 'doc_type', 'doc_number')},
        ),
        migrations.AlterUniqueTogether(
            name='randomdocscan',
            unique_together={('transit', 'doc_name', 'doc_number')},
        ),
    ]