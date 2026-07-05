from django import forms

from .models import AIGenerationTask


class AIGenerationTaskAdminForm(forms.ModelForm):
    class Meta:
        model = AIGenerationTask
        fields = (
            "config",
            "task_type",
            "prompt",
            "image",
            "extra_params",
        )

    def clean_config(self):
        config = self.cleaned_data.get("config")
        if config and not config.is_active:
            raise forms.ValidationError("所选模型配置未启用。")
        return config

    def clean_task_type(self):
        task_type = self.cleaned_data.get("task_type")
        if task_type and task_type != AIGenerationTask.TaskType.VIDEO:
            raise forms.ValidationError("当前仅支持视频生成任务。")
        return task_type
