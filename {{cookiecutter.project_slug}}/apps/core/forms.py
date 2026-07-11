from crispy_forms.helper import FormHelper


class BaseFormHelper(FormHelper):
    """Shared crispy layout defaults; business forms may extend the layout."""

    def __init__(self, *args, css_class: str = "", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.disable_csrf = True
        self.form_show_errors = True
        self.form_class = " ".join(part for part in ("dh-form", css_class) if part)
        self.label_class = "dh-form__label"
        self.field_class = "dh-form__field"
