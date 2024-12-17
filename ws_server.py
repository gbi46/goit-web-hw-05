import asyncio
import json
import logging
import names
import platform
import websockets
from aiofile import AIOFile
from aiopath import AsyncPath
from cli import CLIHandler
from exchangerate import ExchangeRateApp
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)

class Server:
    def __init__(self):
        self.cli_handler = CLIHandler()
        self.exchange_rate_app = ExchangeRateApp()
        self.clients = set()

    async def write_log(self, data):
        log_file = 'exchange_rates.log'
        path = AsyncPath(log_file)
        write_mode = ''

        if not await path.exists():
            write_mode = "w"
        else:
            write_mode = "a"

        write_text = f"\n{data}"

        async with AIOFile(log_file, write_mode) as afp:
                await afp.write(write_text)
                await afp.fsync()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects")

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            format_msg = message.strip()
            if 'exchange' in format_msg:
                args = message.split(' ');
                additional_currencies = ''
                days = 1

                if len(args) > 1:
                    days = args[1].strip()
                    
                if len(args) > 2:
                    additional_currencies = args[2].strip()
                    additional_currencies = additional_currencies.split(',')

                if len(args) > 3:
                    res = json.dumps({"error_msg": "Incorrect count of arguments"})
                else:
                    exchange_rates = await self.exchange_rate_app.fetch_exchange_rates(
                        {
                            'days': days, 
                            'additional_currencies': additional_currencies
                        }
                    )
                    res = self.cli_handler.display_results(exchange_rates)

                await self.send_to_clients(f"{res}")

                formatted_exchange_rates = await self.exchange_rate_app.formatted_exchange_rates(exchange_rates)
                await self.write_log(formatted_exchange_rates)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")
    
async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, '0.0.0.0', 8082):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())