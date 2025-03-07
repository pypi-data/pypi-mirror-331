import json
import os
import pkg_resources

class Nc3:
    currency_map = {}

    @staticmethod
    def load_currencies():
        if not Nc3.currency_map: 
            json_path = pkg_resources.resource_filename(
                __name__, "currencies_lookup.json"
            )
            with open(json_path, "r") as file:
                Nc3.currency_map = json.load(file)

    @staticmethod
    def to_long(short_form):
        Nc3.load_currencies()  
        return Nc3.currency_map.get(short_form.upper(), "Unknown Currency")

    @staticmethod
    def to_short(long_form):
        Nc3.load_currencies() 
        for code, name in Nc3.currency_map.items():
            if name.lower() == long_form.lower():
                return code
        return "Unknown Code"
