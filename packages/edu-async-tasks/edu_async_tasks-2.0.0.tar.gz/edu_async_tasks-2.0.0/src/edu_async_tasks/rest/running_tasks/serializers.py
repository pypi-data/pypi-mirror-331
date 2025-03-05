from rest_framework import (
    serializers,
)
from rest_framework.fields import (
    DurationField,
    SerializerMethodField,
)

from edu_async_tasks.core.models import (
    RunningTask,
)
from edu_async_tasks.core.services import (
    get_running_task_result,
)
from edu_async_tasks.rest.async_task_statuses.serializers import (
    AsyncTaskStatusSerializer,
)


class RunningTaskSerializer(serializers.ModelSerializer):

    status = AsyncTaskStatusSerializer()
    task_result = SerializerMethodField()
    execution_time = DurationField(read_only=True)

    def get_task_result(self, obj):
        task_result = get_running_task_result(obj)

        return {
            'values': task_result.values,
            'error_text': task_result.error
        }

    class Meta:
        model = RunningTask
        fields = (
            'id',
            'queued_at',
            'started_at',
            'name',
            'description',
            'status',
            'task_result',
            'finished_at',
            'execution_time',
        )


class RevokeTasksActionSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )
