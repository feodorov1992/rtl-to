from orders.mailer import FromDatePlanManagerNotification, FromDateFactManagerNotification, \
    ToDatePlanManagerNotification, ToDateFactManagerNotification, OrderCreatedManagerNotification, \
    OrderCreatedClientNotification, FromDatePlanClientNotification, FromDatePlanSenderNotification, \
    FromDateFactClientNotification, ToDatePlanClientNotification, ToDatePlanReceiverNotification, \
    ToDateFactClientNotification
from rtl_to.celery import app


@app.task
def from_date_plan_manager_notification(transit_pk):
    notification = FromDatePlanManagerNotification(transit_pk)
    return notification.send()


@app.task
def from_date_plan_client_notification(transit_pk):
    notification = FromDatePlanClientNotification(transit_pk)
    return notification.send()


@app.task
def from_date_plan_sender_notification(transit_pk):
    notification = FromDatePlanSenderNotification(transit_pk)
    return notification.send()


@app.task
def from_date_fact_manager_notification(transit_pk):
    notification = FromDateFactManagerNotification(transit_pk)
    return notification.send()


@app.task
def from_date_fact_client_notification(transit_pk):
    notification = FromDateFactClientNotification(transit_pk)
    return notification.send()


@app.task
def to_date_plan_manager_notification(transit_pk):
    notification = ToDatePlanManagerNotification(transit_pk)
    return notification.send()


@app.task
def to_date_plan_client_notification(transit_pk):
    notification = ToDatePlanClientNotification(transit_pk)
    return notification.send()


@app.task
def to_date_plan_receiver_notification(transit_pk):
    notification = ToDatePlanReceiverNotification(transit_pk)
    return notification.send()


@app.task
def to_date_fact_manager_notification(transit_pk):
    notification = ToDateFactManagerNotification(transit_pk)
    return notification.send()


@app.task
def to_date_fact_client_notification(transit_pk):
    notification = ToDateFactClientNotification(transit_pk)
    return notification.send()


@app.task
def order_created_for_manager(order_pk):
    notification = OrderCreatedManagerNotification(order_pk)
    return notification.send()


@app.task
def order_created_for_client(order_pk):
    notification = OrderCreatedClientNotification(order_pk)
    return notification.send()
