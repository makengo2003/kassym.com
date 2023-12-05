from rest_framework import serializers

from change_time.models import ChangeTime


class ChangeTimeSerializer(serializers.ModelSerializer):
    dt = serializers.SerializerMethodField("get_change_time_dt_format")

    class Meta:
        model = ChangeTime
        fields = "__all__"

    def get_change_time_dt_format(self, obj):
        return obj.dt.strftime('%d.%m.%Y')
