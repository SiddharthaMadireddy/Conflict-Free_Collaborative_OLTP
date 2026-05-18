import asyncio
from src.cli.commands import cli
from src.network.server import Server

async def run_server():
    server = Server()
    await server.start()

if __name__ == '__main__':
    # Run the server in the background
    server_task = asyncio.create_task(run_server())
    
    # Run the CLI
    cli()
    
    # Cancel the server task when CLI exits
    server_task.cancel()
