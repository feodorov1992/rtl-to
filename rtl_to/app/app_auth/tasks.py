import logging

import requests
from django.utils import timezone
from django.apps import apps
from requests.exceptions import InvalidJSONError

from app_auth.mailer import ContractDepletionManagerNotification
from rtl_to.celery import app


logger = logging.getLogger(__name__)


@app.task
def contract_depletion_for_manager(contract_pk):
    notification = ContractDepletionManagerNotification(contract_pk)
    notification.send()


@app.task
def get_latest_currency_rates():
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    response = requests.get(url, verify=False)
    try:
        rates = response.json()
        CurrencyRate = apps.get_model('app_auth', 'CurrencyRate')
        CurrencyRate.objects.filter(date=timezone.now().date()).delete()
        bulk = CurrencyRate.objects.bulk_create([
            CurrencyRate(
                EUR=rates['Valute']['EUR']['Value'],
                USD=rates['Valute']['USD']['Value'],
                GBP=rates['Valute']['GBP']['Value'],
                INR=rates['Valute']['INR']['Value']
            )
        ])
        obj = bulk[0]
        obj.refresh_from_db()
        logger.info('Rates for {} created. USD: {}; EUR: {}; GBP: {}; INR: {}'.format(
            obj.date.isoformat(),
            obj.USD, obj.EUR, obj.GBP, obj.INR
        ))
    except InvalidJSONError:
        logger.error(f'{response.url} {response.status_code} {response.reason} {response.text}')
        raise
