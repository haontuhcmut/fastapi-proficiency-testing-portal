from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from app.error import register_all_errors
from app.config import Config

from app.auth.route import oauth_route
from app.category.route import category_route
from app.pt_scheme.route import pt_scheme_route
from app.product.route import product_route
from app.bom.route import bom_route
from app.material.route import material_route
from app.warehouse.route import warehouse_route
from app.transaction.route import transaction_route
from app.transaction_detail.route import transaction_detail_route


description = """
A REST API for a Reference Material Product Management Systems web service.

This REST API is able to:
- Create product and inventory management
"""

version_prefix = Config.VERSION

app = FastAPI(
    title="Reference Material Product Management Systems",
    description=description,
    version=version_prefix,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Hao Nguyen",
        "url": "https://github.com/haontuhcmut",
        "email": "nguyenminhhao1188@gmail.com",
    },
    openapi_url=f"/{version_prefix}/openapi.json",
    docs_url=f"/{version_prefix}/docs",
    redoc_url=f"/{version_prefix}/redoc",
)

# Add pagination support
add_pagination(app)

# Add error handling
register_all_errors(app)

# Add route
app.include_router(oauth_route, prefix=f"/{version_prefix}/oauth", tags=["oauth"])
app.include_router(category_route, prefix=f"/{version_prefix}/category", tags=["category"])
app.include_router(pt_scheme_route, prefix=f"/{version_prefix}/pt_scheme", tags=["pt_scheme"])
app.include_router(product_route, prefix=f"/{version_prefix}/product", tags=["product"])
app.include_router(bom_route, prefix=f"/{version_prefix}/bom", tags=["bom"])
app.include_router(material_route, prefix=f"/{version_prefix}/material", tags=["material"])
app.include_router(warehouse_route, prefix=f"/{version_prefix}/warehouse", tags=["warehouse"])
app.include_router(transaction_route, prefix=f"/{version_prefix}/transaction", tags=["transaction"])
app.include_router(transaction_detail_route, prefix=f"/{version_prefix}/transaction_detail", tags=["transaction_detail"])

