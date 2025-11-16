import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem

app = FastAPI(title="Jewelry Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Jewelry Store Backend is running"}

@app.get("/api/products", response_model=List[Product])
def list_products(category: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    try:
        filt = {}
        if category:
            filt["category"] = category
        if q:
            # simple text search across title/description
            filt["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
            ]
        docs = get_documents("product", filt, limit)
        # Map raw docs to Product by selecting fields
        products: List[Product] = []
        for d in docs:
            products.append(Product(
                title=d.get("title", ""),
                description=d.get("description"),
                price=float(d.get("price", 0)),
                category=d.get("category", "Other"),
                in_stock=bool(d.get("in_stock", True)),
                image_url=d.get("image_url"),
                material=d.get("material"),
                gemstones=d.get("gemstones")
            ))
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreateProduct(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
    image_url: Optional[str] = None
    material: Optional[str] = None
    gemstones: Optional[List[str]] = None

@app.post("/api/products")
def create_product(payload: CreateProduct):
    try:
        pid = create_document("product", payload.model_dump())
        return {"id": pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreateOrder(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    items: List[OrderItem]
    total_amount: float
    notes: Optional[str] = None

@app.post("/api/orders")
def create_order(payload: CreateOrder):
    try:
        oid = create_document("order", payload.model_dump())
        return {"id": oid, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
