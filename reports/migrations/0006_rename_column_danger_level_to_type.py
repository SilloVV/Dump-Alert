"""
Migration manuelle : renomme la colonne danger_level → type dans reports_report.

Pourquoi RunSQL et non RenameField ?
Django pense déjà que le champ s'appelle 'type' (migrations 0004/0005 ont
mis à jour l'état interne sans toucher la BDD car seuls choices/verbose_name
changeaient). RenameField échouerait car Django dirait "champ 'type' inexistant".
RunSQL agit directement sur la colonne PostgreSQL.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0005_remove_reportcluster_max_danger_level_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='reports_report' AND column_name='danger_level'
                    ) THEN
                        ALTER TABLE reports_report RENAME COLUMN danger_level TO "type";
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='reports_report' AND column_name='type'
                    ) THEN
                        ALTER TABLE reports_report RENAME COLUMN "type" TO danger_level;
                    END IF;
                END $$;
            """,
        ),
    ]
