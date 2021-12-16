import requests
import json

api_access_token = 'e654a0ca68414149d07a6464a*******'
my_login = '+7903642****'

def create_pay_form(comment, amountInteger=0, amountFraction=0,):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer' + api_access_token

    parameters = {
        'amountInteger': str(amountInteger),
        'amountFraction': str(amountFraction),
        'currency': '643',
        'extra[\'comment\']': str(comment),
        'extra[\'account\']': my_login,
        'blocked': ['sum', 'account', 'comment'],
    }
    return s.get('https://qiwi.com/payment/form/99?', params=parameters).url


def payment_history_last(rows_num, next_TxnId, next_TxnDate):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': rows_num, 'nextTxnId': next_TxnId, 'nextTxnDate': next_TxnDate}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters)
    return h.json()
