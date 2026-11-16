from django.db import migrations


def create_catalog_editors(apps, schema_editor):
    db = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    book_type, _ = ContentType.objects.using(db).get_or_create(
        app_label="catalog", model="book"
    )
    editors, _ = Group.objects.using(db).get_or_create(name="Catalog editors")
    for action in ("add", "change", "delete"):
        permission, _ = Permission.objects.using(db).get_or_create(
            content_type=book_type,
            codename=f"{action}_book",
            defaults={"name": f"Can {action} book"},
        )
        editors.permissions.add(permission)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("catalog", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        # Keep memberships and permission changes made in admin on rollback.
        migrations.RunPython(create_catalog_editors, migrations.RunPython.noop),
    ]
