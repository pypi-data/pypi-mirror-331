from time import (
    sleep,
)

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.test import (
    TestCase,
)

from testapp.app.tasks import (
    lockable_task,
    null_task,
)
from testapp.persons.models import (
    Person,
    UUIDPerson,
)

from edu_async_tasks.core.domain.model import (
    TaskUniqueException,
)
from edu_async_tasks.core.models import (
    RunningTask,
)


class TasksTestCase(TestCase):

    def test_apply_async(self):
        ct = ContentType.objects.get_for_model(Person)
        person = Person.objects.first()

        self.assertIsNotNone(person)

        result = null_task.apply_async(kwargs=dict(profile_type=ct.id, profile_id=person.id))

        running_task = RunningTask.objects.get(id=result.task_id)

        self.assertEqual(running_task.user_profile, person)

    def test_apply_async_nonint_id(self):
        ct = ContentType.objects.get_for_model(UUIDPerson)
        person, _ = UUIDPerson.objects.get_or_create(
            surname='Иванов', firstname='Иван', patronymic='Иванович'
        )
        result = null_task.apply_async(kwargs=dict(profile_type=ct.id, profile_id=person.id))
        running_task = RunningTask.objects.get(id=result.task_id)

        self.assertEqual(running_task.user_profile, person)

    def test_lockable_task(self):
        lock_data = {'lock_expire': 5}

        lockable_task.apply_async(lock_data=lock_data)

        with self.assertRaises(TaskUniqueException):
            lockable_task.apply_async(lock_data=lock_data)

        sleep(lock_data['lock_expire'])

        lockable_task.apply_async(lock_data=lock_data)
