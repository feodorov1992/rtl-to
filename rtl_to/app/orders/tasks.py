from time import sleep

from orders.mailer import FromDatePlanManagerNotification, FromDateFactManagerNotification, \
    ToDatePlanManagerNotification, ToDateFactManagerNotification, OrderCreatedManagerNotification, \
    OrderCreatedClientNotification, FromDatePlanClientNotification, FromDateFactSenderNotification, \
    FromDateFactClientNotification, ToDatePlanClientNotification, ToDateFactReceiverNotification, \
    ToDateFactClientNotification, AddressChangedCarrierNotification, DocumentAddedManagerNotification, \
    DocumentAddedClientNotification, FromDatePlanCarrierNotification, FromDateFactCarrierNotification, \
    ToDatePlanCarrierNotification, ToDateFactCarrierNotification, ExtOrderAssignedCarrierNotification
from rtl_to.celery import app


@app.task
def from_date_plan_manager_notification(transit_pk):
    sleep(1)
    notification = FromDatePlanManagerNotification(transit_pk)
    return notification.send()


@app.task
def from_date_plan_client_notification(transit_pk):
    sleep(1)
    notification = FromDatePlanClientNotification(transit_pk)
    return notification.send()


@app.task
def from_date_fact_sender_notification(transit_pk):
    sleep(1)
    notification = FromDateFactSenderNotification(transit_pk)
    return notification.send()


@app.task
def from_date_plan_carrier_notification(transit_pk):
    sleep(1)
    notification = FromDatePlanCarrierNotification(transit_pk)
    return notification.send()


@app.task
def from_date_fact_manager_notification(transit_pk):
    sleep(1)
    notification = FromDateFactManagerNotification(transit_pk)
    return notification.send()


@app.task
def from_date_fact_client_notification(transit_pk):
    sleep(1)
    notification = FromDateFactClientNotification(transit_pk)
    return notification.send()


@app.task
def from_date_fact_carrier_notification(transit_pk):
    sleep(1)
    notification = FromDateFactCarrierNotification(transit_pk)
    return notification.send()


@app.task
def to_date_plan_manager_notification(transit_pk):
    sleep(1)
    notification = ToDatePlanManagerNotification(transit_pk)
    return notification.send()


@app.task
def to_date_plan_client_notification(transit_pk):
    sleep(1)
    notification = ToDatePlanClientNotification(transit_pk)
    return notification.send()


@app.task
def to_date_fact_receiver_notification(transit_pk):
    sleep(1)
    notification = ToDateFactReceiverNotification(transit_pk)
    return notification.send()


@app.task
def to_date_plan_carrier_notification(transit_pk):
    sleep(1)
    notification = ToDatePlanCarrierNotification(transit_pk)
    return notification.send()


@app.task
def to_date_fact_manager_notification(transit_pk):
    sleep(1)
    notification = ToDateFactManagerNotification(transit_pk)
    return notification.send()


@app.task
def to_date_fact_client_notification(transit_pk):
    sleep(1)
    notification = ToDateFactClientNotification(transit_pk)
    return notification.send()


@app.task
def to_date_fact_carrier_notification(transit_pk):
    sleep(1)
    notification = ToDateFactCarrierNotification(transit_pk)
    return notification.send()


@app.task
def order_created_for_manager(order_pk):
    sleep(1)
    notification = OrderCreatedManagerNotification(order_pk)
    return notification.send()


@app.task
def order_created_for_client(order_pk):
    sleep(1)
    notification = OrderCreatedClientNotification(order_pk)
    return notification.send()


@app.task
def address_changed_for_carrier(ext_order_pk):
    sleep(1)
    notification = AddressChangedCarrierNotification(ext_order_pk)
    return notification.send()


@app.task
def document_added_for_manager(doc_pk):
    sleep(1)
    notification = DocumentAddedManagerNotification(doc_pk)
    return notification.send()


@app.task
def document_added_for_client(doc_pk):
    sleep(1)
    notification = DocumentAddedClientNotification(doc_pk)
    return notification.send()


@app.task
def ext_order_assigned_carrier_notification(ext_order_pk):
    sleep(1)
    notification = ExtOrderAssignedCarrierNotification(ext_order_pk)
    return notification.send()
