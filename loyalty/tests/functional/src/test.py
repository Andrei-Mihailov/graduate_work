import pytest
from fastapi.testclient import TestClient
from main import app
from utils.auth import security_jwt
from services.purchase_service import PurchaseService
from services.promo_code_service import PromoCodeService

client = TestClient(app)

@pytest.fixture
def mock_user():
    return {"id": 1, "username": "testuser"}

@pytest.fixture
def mock_purchase_service(mocker):
    purchase_service = mocker.Mock(spec=PurchaseService)
    mocker.patch("main.get_purchase_service", return_value=purchase_service)
    return purchase_service

@pytest.fixture
def mock_promo_code_service(mocker):
    promo_code_service = mocker.Mock(spec=PromoCodeService)
    mocker.patch("main.get_promo_code_service", return_value=promo_code_service)
    return promo_code_service

@pytest.fixture
def mock_security_jwt(mocker, mock_user):
    mocker.patch("main.security_jwt", return_value=mock_user)

def test_apply_promocode(mock_security_jwt, mock_purchase_service, mock_promo_code_service):
    mock_purchase_service.get_instance_by_id.return_value = {"id": 1, "price": 100.0}
    mock_promo_code_service.get_valid_promocode.return_value = {"discount_type": "fixed", "discount": 10.0}
    mock_purchase_service.calculate_final_amount.return_value = 90.0

    response = client.post("/apply_promocode/", json={"promocode": "TESTCODE", "tariff_id": 1})
    assert response.status_code == 200
    assert response.json() == {
        "discount_type": "fixed",
        "discount_value": 10.0,
        "final_amount": 90.0
    }

def test_get_active_promocodes(mock_security_jwt, mock_promo_code_service):
    mock_promo_code_service.get_active_promocodes_for_user.return_value = [
        {"code": "PROMO1", "discount_type": "fixed", "discount_value": 10.0, "expiration_date": "2023-12-31T00:00:00"}
    ]

    response = client.get("/get_active_promocodes/")
    assert response.status_code == 200
    assert response.json() == [
        {"code": "PROMO1", "discount_type": "fixed", "discount_value": 10.0, "expiration_date": "2023-12-31T00:00:00"}
    ]

def test_use_promocode(mock_security_jwt, mock_purchase_service, mock_promo_code_service):
    mock_purchase_service.use_promocode.return_value = {
        "discount_type": "fixed",
        "discount_value": 10.0,
        "final_amount": 90.0
    }

    response = client.post("/use_promocode/", json={"promocode": "TESTCODE", "tariff_id": 1})
    assert response.status_code == 200
    assert response.json() == {
        "discount_type": "fixed",
        "discount_value": 10.0,
        "final_amount": 90.0
    }

def test_cancel_use_promocode(mock_security_jwt, mock_purchase_service):
    mock_purchase_service.get_purchase.return_value = {"id": 1, "price": 100.0}
    mock_purchase_service.cancel_purchase.return_value = 100.0

    response = client.post("/cancel_use_promocode/", json={"promocode": 1, "purchase_id": 1})
    assert response.status_code == 200
    assert response.json() == {
        "discount_type": None,
        "discount_value": 0,
        "final_amount": 100.0
    }
