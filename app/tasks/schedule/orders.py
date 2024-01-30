import datetime

from app.tasks import celery_app


@celery_app.task
def check_new_orders():
    with open('app/tasks/start123.txt', 'w') as f:
        f.write(str(datetime.datetime.utcnow()))
