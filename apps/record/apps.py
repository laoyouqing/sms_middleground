from django.apps import AppConfig


class RecordConfig(AppConfig):
    name = 'apps.record'
    verbose_name = "推送管理"

    def ready(self):
        import record.signals
