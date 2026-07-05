from django.db import migrations, models


def migrate_verified_identities(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    EmailAddress = apps.get_model("account", "EmailAddress")
    for user in User.objects.all().iterator():
        update_fields = []
        if user.phone and not user.phone_verified:
            user.phone_verified = True
            update_fields.append("phone_verified")
        if update_fields:
            user.save(update_fields=update_fields)
        email = (user.email or "").strip().lower()
        if email and not email.endswith("@mobile.__INVALID_EMAIL_DOMAIN__"):
            EmailAddress.objects.update_or_create(
                user_id=user.pk,
                email=email,
                defaults={"primary": True, "verified": True},
            )


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0009_emailaddress_unique_primary_email"),
        ("accounts", "0003_user_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone_verified",
            field=models.BooleanField(default=False, verbose_name="手机号已验证"),
        ),
        migrations.RunPython(
            migrate_verified_identities,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
