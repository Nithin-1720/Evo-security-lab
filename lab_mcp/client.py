import asyncio

from mcp import Client


MCP_URL = "http://127.0.0.1:8001/mcp"


async def main():

    async with Client(MCP_URL) as client:

        print("Connected to MCP server")
        print()

        tools = await client.list_tools()

        print("Available tools:")

        for tool in tools.tools:
            print(f" - {tool.name}")

        print()

        resources = await client.list_resources()

        print("Available resources:")

        for resource in resources.resources:
            print(f" - {resource.uri}")

        print()

        result = await client.call_tool(
            "lookup_demo_customer",
            {
                "customer_id": 1001,
            },
        )

        print("Tool result:")
        print(result)

        print()

        policy = await client.read_resource(
            "lab://support-policy"
        )

        print("Resource result:")

        for content in policy.contents:

            if hasattr(content, "text"):
                print(content.text)


if __name__ == "__main__":

    asyncio.run(main())