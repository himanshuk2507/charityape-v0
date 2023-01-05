from subprocess import run as run_script, PIPE

from flask import Blueprint

from src.library.seeders.admin import seed_admin


custom_cli_commands = Blueprint('cli', __name__)

@custom_cli_commands.cli.command('start_celery')
def start_celery():
    print('** Starting Celery worker in background **')
    
    command = "celery --app run.celery worker --loglevel=debug"
    run_script(command.split(' '), stdout=PIPE, text=True)


@custom_cli_commands.cli.command('seed')
def seed_database():
    print('** Seeding database **')
    seed_admin()