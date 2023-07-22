from orders.mailer import FromDatePlanManagerNotification, FromDateFactManagerNotification, \
    ToDatePlanManagerNotification, ToDateFactManagerNotification
from rtl_to.celery import app


@app.task
def from_date_plan_manager_notification(transit_pk):
    notification = FromDatePlanManagerNotification(transit_pk)
    return notification.send()


@app.task
def from_date_fact_manager_notification(transit_pk):
    notification = FromDateFactManagerNotification(transit_pk)
    return notification.send()


@app.task
def to_date_plan_manager_notification(transit_pk):
    notification = ToDatePlanManagerNotification(transit_pk)
    return notification.send()


@app.task
def to_date_fact_manager_notification(transit_pk):
    notification = ToDateFactManagerNotification(transit_pk)
    return notification.send()
