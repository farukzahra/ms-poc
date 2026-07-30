from __future__ import annotations

import os

import uvicorn

from shared.mock_apps import (
    create_contracts_app,
    create_crm_app,
    create_products_app,
    create_sales_app,
    create_tickets_app,
)

APPS = {
    "crm": create_crm_app,
    "sales": create_sales_app,
    "tickets": create_tickets_app,
    "contracts": create_contracts_app,
    "products": create_products_app,
}


def main() -> None:
    service = os.environ.get("MOCK_SERVICE", "crm")
    port = int(os.environ.get("PORT", "8101"))
    factory = APPS.get(service)
    if not factory:
        raise SystemExit(f"Unknown MOCK_SERVICE: {service}")
    uvicorn.run(factory(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
