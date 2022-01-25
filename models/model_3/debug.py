from iqoptionapi.stable_api import IQ_Option
import timeout
import time


connector =IQ_Option("levanmikeladze123@gmail.com" ,"591449588")
connector.connect()
connector.change_balance("PRACTICE")
iqcomb = [("NZD", "SEK"),("NZD", "USD"),("CAD", "TRY"),("EUR", "CHF"),("USD", "THB"),("EUR", "TRY"),("GBP", "AUD"),("AUD", "USD"),("EUR", "MXN"),("USD", "CHF"),("NOK", "DKK"),("EUR", "NOK"),("SEK", "JPY"),("CAD", "NOK"),("NOK", "SEK"),("GBP", "HUF"),("GBP", "SGD"),("AUD", "NZD"),("GBP", "JPY"),("CHF", "SEK"),("AUD", "NOK"),("GBP", "NOK"),("AUD", "DKK"),("EUR", "AUD"),("AUD", "CHF"),("GBP", "CHF"),("AUD", "CAD"),("CHF", "DKK"),("AUD", "TRY"),("NZD", "CHF"),("USD", "SEK"),("GBP", "NZD"),("EUR", "DKK"),("NZD", "DKK"),("CAD", "SGD"),("EUR", "GBP"),("EUR", "CAD"),("USD", "CZK"),("AUD", "MXN"),("EUR", "NZD"),("GBP", "PLN"),("NZD", "NOK"),("AUD", "SGD"),("GBP", "SEK"),("NZD", "CAD"),("NZD", "MXN"),("NZD", "TRY"),("CHF", "SGD"),("USD", "MXN"),("EUR", "HUF"),("GBP", "CAD"),("USD", "TRY"),("USD", "JPY"),("EUR", "USD"),("AUD", "SEK"),("CHF", "NOK"),("USD", "PLN"),("USD", "HUF"),("CHF", "JPY"),("GBP", "ILS"),("NZD", "JPY"),("CHF", "TRY"),("CAD", "JPY"),("USD", "RUB"),("SGD", "JPY"),("GBP", "USD"),("CAD", "PLN"),("DKK", "SGD"),("NZD", "SGD"),("AUD", "JPY"),("NOK", "JPY"),("PLN", "SEK"),("USD", "SGD"),("GBP", "MXN"),("USD", "CAD"),("SEK", "DKK"),("DKK", "PLN"),("CAD", "MXN"),("GBP", "TRY"),("EUR", "SGD"),("NZD", "ZAR"),("EUR", "CZK"),("EUR", "JPY"),("CAD", "CHF"),("USD", "INR"),("USD", "BRL"),("USD", "NOK"),("USD", "DKK")]

while True:
    print(timeout.custom_profit(connector, ['forex',])[0])
