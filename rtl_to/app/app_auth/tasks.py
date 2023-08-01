from app_auth.mailer import ContractDepletionManagerNotification
from rtl_to.celery import app


@app.task
def contract_depletion_for_manager(contract_pk):
    notification = ContractDepletionManagerNotification(contract_pk)
    notification.send()
