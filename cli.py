import argparse
import json
from currency import Currency
from typing import Dict

class CLIHandler:    
    def parse_arguments(self):
        currency = Currency
        list_of_currencies = currency.get_available_list()

        parser = argparse.ArgumentParser(description="Request currency exchange for last several days")
        
        parser.add_argument(
            'days',
            type=int,
            nargs='?',
            default=1,
            help="Will get currency exchange course for last days (max. 10)."
        )

        parser.add_argument(
            'additional_currencies',
            type=str,
            nargs='?',
            help=f"List of currencies: {list_of_currencies}",
            default="EUR, USD"
        )
        
        args = parser.parse_args()
        
        if args.days < 1 or args.days > 10:
            parser.error("Count of days must be from 1 to 10")

        currencies = [currency.strip().upper() for currency in args.additional_currencies.split(",")]
        
        return {
            'days': args.days,
            'additional_currencies': currencies
        }

    def display_results(self, results: Dict[str, Dict]):
        return json.dumps(results, indent=4)