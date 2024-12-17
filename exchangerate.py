import aiohttp
import asyncio
import json
from cli import CLIHandler
from datetime import datetime, timedelta
from typing import Dict

class ExchangeRateApi:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date={}"

    async def get_rate(self, session:aiohttp.ClientSession, date: str, retries: int = 3) -> dict:
        url = self.BASE_URL.format(date)
        for attempt in range(retries):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientConnectionError:
                print(f"Connection error for {date}. Try {attempt + 1} from {retries} retries")
            except aiohttp.ClientResponseError as e:
                print(f"Server error ({e.status}) for {date}: {e.message}")
                break
            except asyncio.TimeoutError:
                print(f"Timeout error for {date}. Try {attempt + 1} from {retries}")
            except aiohttp.ClientError as e:
                print(f"Error while request to {date}: {e}")
            except Exception as e:
                print(f"An unknown error occured: {e}")
                break
        print(f"Error while request for {date}.")
        return {}

class ExchangeRateProcessor:
    def process_exchange_rate(self, data: Dict, additional_currencies=False) -> Dict[str, Dict[str, float]]:
        if not data or 'exchangeRate' not in data:
            return {}

        currencies = ['EUR', 'USD']

        if additional_currencies:
            currencies = currencies + additional_currencies
        
        result = {}
        for item in data['exchangeRate']:
            if item.get('currency') in currencies:
                result[item['currency']] = {
                    'purchase': item.get('purchaseRate', 'N/A'),
                    'sale': item.get('saleRate', 'N/A')
                }
        return result
    
class ExchangeRateApp:
    def __init__(self):
        self.api_client = ExchangeRateApi()
        self.processor = ExchangeRateProcessor()
        self.cli_handler = CLIHandler()

    async def fetch_exchange_rates(self, args: dict) -> dict:
        today = datetime.now()

        days = int(args['days'])

        additional_currencies = False
        if 'additional_currencies' in args.keys():
            additional_currencies = args['additional_currencies']                

        dates = [(today - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(days)]
        results = {"resp_type" : "currencies", "resp_view" : "table", "currenciesData" : {}, "message": ""}

        if(days < 1 or days > 10):
            results['resp_type'] = 'error'
            results["message"] = 'Error: count of days must be from 1 to 10'
        else:
            async with aiohttp.ClientSession() as session:
                tasks = [self.api_client.get_rate(session, date) for date in dates]
                responses = await asyncio.gather(*tasks)
                
                for date, data in zip(dates, responses):
                    if data:
                        processed_data = self.processor.process_exchange_rate(data, additional_currencies)
                        if processed_data:
                            results['currenciesData'][date] = processed_data
                    else:
                        print(f"No data for {date} available")
        
        return results
    
    async def formatted_exchange_rates(self, rates):
        exchange_rates = rates['currenciesData']
        formatted_rates = json.dumps(exchange_rates, indent=4)

        return formatted_rates

    def run(self):
        args = self.cli_handler.parse_arguments()
        results = asyncio.run(self.fetch_exchange_rates(args))
        print(self.cli_handler.display_results(results['currenciesData']))
