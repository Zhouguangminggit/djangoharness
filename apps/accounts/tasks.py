from celery import shared_task


@shared_task
def send_welcome_email(username):
    return f"welcome {username}"
