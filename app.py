
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

deliveries = {}
next_id = 1
VALID_STATUSES = ["created", "in_transit", "delivered"]


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request"}
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/deliveries", status_code=201)
def create_delivery(data: dict = Body(...)):
    global next_id

    recipient = data.get("recipient")
    address = data.get("address")

    if not isinstance(recipient, str) or not recipient.strip():
        return JSONResponse(status_code=400, content={"error": "Invalid recipient"})

    if not isinstance(address, str) or not address.strip():
        return JSONResponse(status_code=400, content={"error": "Invalid address"})

    delivery = {
        "id": next_id,
        "recipient": recipient,
        "address": address,
        "status": "created"
    }
    deliveries[next_id] = delivery
    next_id += 1
    return delivery


@app.get("/deliveries")
def list_deliveries(status: str = None):
    if status is not None and status not in VALID_STATUSES:
        return JSONResponse(status_code=400, content={"error": "Invalid status"})

    result = list(deliveries.values())
    if status is not None:
        result = [d for d in result if d["status"] == status]
    return result


@app.get("/deliveries/{delivery_id}")
def get_delivery(delivery_id: int):
    delivery = deliveries.get(delivery_id)
    if delivery is None:
        return JSONResponse(status_code=404, content={"error": "Delivery not found"})
    return delivery


@app.patch("/deliveries/{delivery_id}/status")
def update_delivery_status(delivery_id: int, data: dict = Body(...)):
    delivery = deliveries.get(delivery_id)
    if delivery is None:
        return JSONResponse(status_code=404, content={"error": "Delivery not found"})

    new_status = data.get("status")
    if new_status not in VALID_STATUSES:
        return JSONResponse(status_code=400, content={"error": "Invalid status"})

    current_index = VALID_STATUSES.index(delivery["status"])
    new_index = VALID_STATUSES.index(new_status)

    if new_index != current_index + 1:
        return JSONResponse(status_code=409, content={"error": "Invalid status transition"})

    delivery["status"] = new_status
    return delivery


@app.delete("/deliveries/{delivery_id}", status_code=204)
def delete_delivery(delivery_id: int):
    delivery = deliveries.get(delivery_id)
    if delivery is None:
        return JSONResponse(status_code=404, content={"error": "Delivery not found"})

    if delivery["status"] != "created":
        return JSONResponse(status_code=409, content={"error": "Cannot delete this delivery"})

    del deliveries[delivery_id]
    return None
