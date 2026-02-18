from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


sample_product_1 = {
    "product_id": 123,
    "name": "Artyrchik",
    "category": "Mega_swag",
    "price": 599999999.99
}
sample_product_2 = {
    "product_id": 456,
    "name": "Artyr",
    "category": "sex",
    "price": 999999999.99
}
sample_products = [
    sample_product_1,
    sample_product_2,
]
@app.get("/product/{product_id}", response_model=Product)
async def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(
        status_code=404,
        detail=f"Продукт с ID {product_id} не найден"
    )
@app.get("/products/search", response_model=List[Product])
async def search_products(
    keyword: str = Query(..., description="Ключевое слово для поиска (обязательно)"),
    category: Optional[str] = Query(None, description="Категория для фильтрации (необязательно)"),
    limit: int = Query(10, ge=1, description="Максимальное количество результатов (по умолчанию 10)")
):
    results = [] 
    for product in sample_products:
        if keyword.lower() not in product["name"].lower():
            continue
        if category and product["category"] != category:
            continue      
        results.append(product)
        if len(results) >= limit:
            break
    return results