from datetime import timedelta
from flask import Blueprint

from skraggle.utils.background_workers.worker_class import BackgroundJob
from .smarkask import smart_ask_worker

workers = Blueprint('workers', __name__)

'''
`flask workers` can be used to initialize workers used throughout the app
'''
# @workers.cli.command('workers')
def initialize_workers():
    # store a reference to each job in the spool
    jobs = dict(
        print_icheka = BackgroundJob(
            smart_ask_worker,
            handler_arguments=["hey"],
            repeat = True,
            # interval = timedelta(minutes=1),
            name = 'print_icheka'
        )
    )
    
    print('Initialized workers')