from redis import Redis
import rq
from time import sleep

from sqlalchemy import Interval
from skraggle.run import app

worker_queue = rq.Queue('worker-tasks', connection = Redis.from_url(app.config['CACHE_REDIS_URL']))
enqueue = worker_queue.enqueue
# enqueue = print
worker_queue.empty()

def default_handler():
    print('Default BackgroundJob handler')

class BackgroundJob:
    def __init__(
            self, handler = default_handler, handler_arguments = None,
            repeat = False, interval = None, run_immediately = True, name = 'job'
        ) -> None:
        self.job = None
        self.handler = handler
        self.handler_arguments = handler_arguments
        self.repeat = repeat 
        self.interval = interval
        self.run_immediately = run_immediately
        self.name = name

        if repeat and not interval:
            # raise '`interval` must be provided with `repeat`'
            return

        if run_immediately and not repeat:
            print('will enqueue new job ->', self.name)
            self.enqueue_job()
        elif repeat:
            print('will enqueue new job ->', self.name)
            self.enqueue_scheduled_job()

    def enqueue_job(self):
        print('enqueueing background job ->', self.name)
        self.job = enqueue(self.handler, self.handler_arguments)

    def enqueue_scheduled_job(self):
        self.handler(self.handler_arguments)

        # enqueue again
        worker_queue.enqueue_in(self.interval, self.enqueue_scheduled_job)
