from flask import Blueprint, render_template, request, redirect, jsonify
import requests
import json

donationsetupiew = Blueprint("donationsetupiew", __name__)


@donationsetupiew.route("/select_currency", methods=["GET"])
def select_currency():
    with open("base_helpers/currencies.json", "r", encoding="utf8", errors="ignore") as file:
        currencies = json.load(file)
        d_currency = requests.get("https://ipapi.co/currency/").text
        d_symbol = (
            currencies[d_currency]["symbol"] if d_currency in currencies else "NA"
        )
        d_curr_name = (
            currencies[d_currency]["name"] if d_currency in currencies else "NA"
        )

        default_currency = {
            "Default_Currency": {
                "Currency": d_currency,
                "Symbol": d_symbol,
                "Currency_name": d_curr_name,
            }
        }

        other_currency = {
            "Other_Currencies": [
                {
                    "Currency": currency,
                    "Currency_name": symbols["name"],
                    "Symbol": symbols["symbol_native"],
                }
                for currency, symbols in currencies.items()
            ]
        }

    return jsonify(default_currency, other_currency)
