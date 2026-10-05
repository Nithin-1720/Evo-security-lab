import asyncio
import sys

from mcp import (
    ClientSession,
    StdioServerParameters,
)

from mcp.client.stdio import stdio_client


server_params = StdioServerParameters(
    command=sys.executable,
    args=[
        "-m",
        "lab_mcp.server_stdio",
    ],
)


async def run():

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            resources = await session.list_resources()

            print(tools)
            print(resources)


if __name__ == "__main__":
    asyncio.run(run())