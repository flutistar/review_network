from celery.task.schedules import crontab
from celery.decorators import periodic_task, task
from celery.utils.log import get_task_logger

from .utils import checkTaskStatus, remindPurchasedProof, send_cancellation_email

logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(minute='*/5')),
    name="celery_check_task_status",
    ignore_result=True
)
def celery_check_task_status():
    checkTaskStatus()
    logger.info("Checked the status of the tasks")

@task(name="send_feedback_email_task")
def send_cancellation_email_task(email, task_id):
    logger.info("Sent feedback email")
    return send_cancellation_email(email, task_id)

@periodic_task(
    run_every=(crontab(minute=0, hour='*/20')),
    name="check_completed_tasks",
    ignore_result=True
)
def check_completed_tasks(): 
    remindPurchasedProof()
    logger.info("Completed takss") 
    