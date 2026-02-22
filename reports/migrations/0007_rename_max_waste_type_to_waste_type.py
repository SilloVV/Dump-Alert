from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0006_rename_column_danger_level_to_type"),
    ]

    operations = [
        migrations.RenameField(
            model_name="reportcluster",
            old_name="max_waste_type",
            new_name="waste_type",
        ),
    ]
