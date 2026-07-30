from mcp_server.config import settings
from mcp_server.tools import server


def main() -> None:
    server.run(
        transport="streamable-http",
        host=settings.mcp_host,
        port=settings.mcp_port,
    )


if __name__ == "__main__":
    main()
