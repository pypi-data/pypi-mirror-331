from time import (
    sleep,
)

from testapp.entrypoints.celery import (
    app,
)

from edu_async_tasks.core.tasks import (
    AsyncTask,
)


class NullTask(AsyncTask):

    def process(self, *args, **kwargs):
        return super().process(*args, **kwargs)


null_task = NullTask()


app.register_task(null_task)


class SleepTask(AsyncTask):

    def process(self, *args, n=5, **kwargs):
        print(f'Sleeping {n} seconds..')
        sleep(n)
        print('..done')
        return super().process(*args, **kwargs)


sleep_task = SleepTask()


app.register_task(sleep_task)


class LockableTask(NullTask):

    locker_config = {
        'lock_params': {'school_id': 1745},
    }


lockable_task = LockableTask()


app.register_task(lockable_task)
