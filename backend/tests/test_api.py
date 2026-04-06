from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"


def test_prioritize_endpoint():
    payload = {
        "batch_id": "batch-test-001",
        "orders": [
            {
                "order_id": "ORD-A",
                "product_name": "Amoxicillin 500mg",
                "quantity": 120,
                "customer_tier": "platinum",
                "urgency_flag": True,
                "stock_available": 90,
                "expiry_date": "2026-05-01",
                "customer_location": "Dublin",
                "warehouse_location": "Dublin",
                "order_date": "2026-04-05",
            },
            {
                "order_id": "ORD-B",
                "product_name": "Metformin 1000mg",
                "quantity": 80,
                "customer_tier": "gold",
                "urgency_flag": False,
                "stock_available": 200,
                "expiry_date": "2026-09-01",
                "customer_location": "Cork",
                "warehouse_location": "Galway",
                "order_date": "2026-04-05",
            },
            {
                "order_id": "ORD-C",
                "product_name": "Insulin Glargine",
                "quantity": 60,
                "customer_tier": "standard",
                "urgency_flag": True,
                "stock_available": 60,
                "expiry_date": "2026-04-25",
                "customer_location": "Limerick",
                "warehouse_location": "Limerick",
                "order_date": "2026-04-05",
            },
        ],
    }
    response = client.post("/orders/prioritize", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["batch_id"] == "batch-test-001"
    assert body["total_orders"] == 3
    assert len(body["decisions"]) == 3


def test_upload_csv_endpoint():
    csv_content = (
        "order_id,product_name,quantity,customer_tier,urgency_flag,stock_available,"
        "expiry_date,customer_location,warehouse_location,order_date\n"
        "ORD-CSV-1,Atorvastatin 40mg,100,gold,true,80,2026-05-01,Dublin,Dublin,2026-04-05\n"
        "ORD-CSV-2,Lisinopril 10mg,50,standard,false,120,2026-08-11,Cork,Galway,2026-04-05\n"
    )
    files = {"file": ("sample.csv", csv_content, "text/csv")}
    response = client.post("/orders/upload-csv", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["total_orders"] == 2
    assert len(body["decisions"]) == 2
