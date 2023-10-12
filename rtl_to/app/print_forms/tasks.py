from print_forms.mailer import TransportAddedManagerNotification, TransportAddedClientNotification, \
    TransportChangedManagerNotification, TransportChangedClientNotification
from rtl_to.celery import app


@app.task
def transport_added_for_manager(docdata_pk):
    notification = TransportAddedManagerNotification(docdata_pk)
    return notification.send()


@app.task
def transport_added_for_client(docdata_pk):
    notification = TransportAddedClientNotification(docdata_pk)
    return notification.send()


@app.task
def transport_changed_for_manager(docdata_pk):
    notification = TransportChangedManagerNotification(docdata_pk)
    return notification.send()


@app.task
def transport_changed_for_client(docdata_pk):
    notification = TransportChangedClientNotification(docdata_pk)
    return notification.send()
