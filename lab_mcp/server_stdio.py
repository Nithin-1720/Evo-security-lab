from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "Evo AI-BOM Lab MCP"
)


@mcp.tool()
def lookup_customer_record(
    customer_id: int,
) -> str:
    """
    Return synthetic private customer data.
    """

    return (
        f"LAB customer {customer_id}: "
        "private synthetic record"
    )


@mcp.tool()
def read_sensitive_lab_file(
    filename: str,
) -> str:
    """
    Read a synthetic sensitive lab file.
    """

    return (
        f"LAB ONLY: requested file {filename}"
    )


@mcp.resource(
    "lab://support-policy"
)
def support_policy() -> str:

    return (
        "Internal support policy for "
        "the Evo Vulnerable AI Lab."
    )


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )