from django import forms
from django.contrib.auth import get_user_model

from .models import NotificationPublication

User = get_user_model()


class NotificationPublicationAdminForm(forms.ModelForm):
    class Meta:
        model = NotificationPublication
        fields = (
            "title",
            "body",
            "level",
            "target_path",
            "audience",
            "recipients",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "recipients" in self.fields:
            recipients_field = self.fields["recipients"]
            assert isinstance(recipients_field, forms.ModelMultipleChoiceField)
            recipients_field.queryset = User.objects.filter(is_active=True).order_by(
                "username"
            )

    def clean(self):
        cleaned_data = super().clean() or {}
        if cleaned_data.get(
            "audience"
        ) == NotificationPublication.Audience.SELECTED and not cleaned_data.get(
            "recipients"
        ):
            self.add_error("recipients", "选择“指定用户”时至少需要选择一名用户。")
        return cleaned_data
