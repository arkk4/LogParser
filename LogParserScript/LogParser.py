import argparse
import json
import os
import pytz
from datetime import datetime 
from collections import Counter
from pytz import timezone

def convert_epoch_to_eet(epoch_time):
    utc_time = datetime.fromtimestamp(epoch_time, pytz.utc)
    eet_timezone = pytz.timezone('Europe/Kiev')
    eet_time = utc_time.astimezone(eet_timezone).strftime('%H%M')
    return eet_time

def date_check(timestamps):
    dates = []
    last_date = None
    for timestamp in timestamps:
        date = datetime.fromtimestamp(int(timestamp) / 1000, timezone('EET')).date()
        dates.append(date)
        last_date = date  

    unique_dates = []
    for timestamp in timestamps:
        date = datetime.fromtimestamp(int(timestamp) / 1000, timezone('EET'))
        if date.date() != last_date:
            formatted_date = f"{timestamp} ({date.date()})"
            unique_dates.append(formatted_date)

    return unique_dates

def duplicates_check(receiptsId):
    count = Counter(receiptsId)
    return [item for item, count in count.items() if count > 1]

def handle_json(json_str):
    parsed_json = json.loads(json_str)
    action = parsed_json.get("deviceAction", '')
    log_data = parsed_json.get("log", {})
    companyName = parsed_json.get("data", {}).get("companyName")
    if action == "printXReport":
        cashflowIncome = log_data.get("reportStats", {}).get("cashflow", {}).get("cashflowIncome")
        cashflowOutcome = log_data.get("reportStats", {}).get("cashflow", {}).get("cashflowOutcome")
        receiptCounter = log_data.get("reportStats", {}).get("receiptCounter")
        total = log_data.get("reportStats", {}).get("total")
        receiptsId = log_data.get("reportStats", {}).get("receiptsId", [])
        unique_dates = date_check(receiptsId)
        duplicate_ids = duplicates_check(receiptsId)

        print(f"X-звіт: {companyName}")

        print(f"Внесення: {cashflowIncome}")
        print(f"Видача: {cashflowOutcome}")
        print(f"Кількість чеків: {receiptCounter}")
        print(f"Всього оплат: {total}")
        print(f"Унікальні дати в чеках: {unique_dates}")
        print(f"Дублікати ID чеків: {duplicate_ids}")

    elif action == "printZReport":
        eventlog = log_data.get("eventLog", {})
        cashflowIncome = eventlog.get("shiftReport", {}).get("totalIncomeCashflow")
        cashflowOutcome = eventlog.get("shiftReport", {}).get("totalOutcomeCashflow")

        print(f"Z-звіт: {companyName}")

        print(f"Внесення: {cashflowIncome}")
        print(f"Видача: {cashflowOutcome}")

    elif action == "printFiscalReceipt":
        eventlog = log_data.get("eventLog", {})
        device_data = eventlog.get("device", {})
        data_id = eventlog.get("data", {}).get("id")
        receiptNumber = eventlog.get("data", {}).get("orderName")
        fiscalData = parsed_json.get("data", {})
        fiscalId = fiscalData.get("id", {})
        fiscalDate = fiscalData.get("fiscalDate", {})
        fiscalNumber = fiscalData.get("fiscalNumber", {})
        fiscalSum = fiscalData.get("amount", {})
        dateClose = eventlog.get("data", {}).get("dateClose")
        datePrint = eventlog.get("data", {}).get("datePrint")
        productsName = eventlog.get("data", {}).get("products", [])
        if datePrint == 0:
            dateClose = dateClose / 1000
            fiscalTime = convert_epoch_to_eet(dateClose)
        else:
            datePrint = datePrint / 1000
            fiscalTime = convert_epoch_to_eet(datePrint)

        fiscalUrl = f"https://cabinet.tax.gov.ua/cashregs/check?id={fiscalId}&date={fiscalDate}&fn={fiscalNumber}&sm={fiscalSum}&time={fiscalTime}"
        
        print(f"Друк чека: {companyName}")

        print(f"Чек: {receiptNumber}")
        print(f"ID: {data_id}")
        print(f"URL: {fiscalUrl}")
        for product in productsName:
            productName = product["name"]
            productCount = product["count"]
            productPrice = product["price"]
            productTax = product["taxName"]


parser = argparse.ArgumentParser()
parser.add_argument("json_input", help="Вхідний JSON")
args = parser.parse_args()
os.system('clear')
handle_json(args.json_input)
