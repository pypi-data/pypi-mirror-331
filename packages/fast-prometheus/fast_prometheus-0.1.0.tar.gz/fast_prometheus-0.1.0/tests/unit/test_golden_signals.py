import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from fast_prometheus import create_prometheus_metrics


def test_request_total() -> None:
    app = FastAPI()
    @app.get('/', status_code=200)
    def test_endpoint() -> None:
        return
    
    @app.get('/error')  # type: ignore
    def test_endpoint() -> None:
        raise HTTPException(status_code=500)
    
    create_prometheus_metrics(app)

    client = TestClient(app)
    for _ in range(5):
        client.get('/')
    for _ in range(4):
        client.get('/error')

    res = client.get('/metrics')    
    assert res.status_code == 200
    assert b'app_requests_total{endpoint="/",method="GET",status="200"} 5.0' in res.content
    assert b'app_active_requests_total{endpoint="/metrics",method="GET"} 1.0' in res.content
    assert b'app_request_duration_seconds_bucket{endpoint="/error",le="0.01",method="GET",status="500"}' in res.content
    assert b'app_memory_percent' in res.content
    assert b'app_cpu_percent' in res.content
    assert b'app_errors_total counter\napp_errors_total{endpoint="/error",method="GET",status="500"} 4.0' in res.content
