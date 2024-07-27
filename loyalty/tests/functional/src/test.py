import pytest

from http import HTTPStatus
from services.purchase_service import PurchaseService
from services.promo_code_service import PromoCodeService

from ..settings import test_settings

SERVICE_URL = test_settings.SERVICE_URL


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


async def test_apply_promocode(make_post_request, mock_purchase_service, mock_promo_code_service):
    mock_purchase_service.get_instance_by_id.return_value = {"id": 1, "price": 100.0}
    mock_promo_code_service.get_valid_promocode.return_value = {"discount_type": "fixed", "discount": 10.0}
    mock_purchase_service.calculate_final_amount.return_value = 90.0
    query_data = {"promocode": "TESTCODE", "tariff_id": 1}
    url = SERVICE_URL + "/api/v1/promocodes/apply_promocode/"
    response = await make_post_request(url, query_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "discount_type": "fixed",
        "discount_value": 10.0,
        "final_amount": 90.0
    }


async def test_get_active_promocodes(make_get_request, mock_promo_code_service):
    mock_promo_code_service.get_active_promocodes_for_user.return_value = [
        {"code": "PROMO1", "discount_type": "fixed", "discount_value": 10.0, "expiration_date": "2023-12-31T00:00:00"}
    ]
    url = SERVICE_URL + "/api/v1/promocodes/get_active_promocodes/"
    response = await make_get_request(url)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {"code": "PROMO1", "discount_type": "fixed", "discount_value": 10.0, "expiration_date": "2023-12-31T00:00:00"}
    ]


async def test_use_promocode(make_post_request, mock_purchase_service, mock_promo_code_service):
    mock_purchase_service.use_promocode.return_value = {
        "discount_type": "fixed",
        "discount_value": 10.0,
        "final_amount": 90.0
    }

    query_data = {"promocode": "TESTCODE", "tariff_id": 1}
    url = SERVICE_URL + "/api/v1/promocodes/use_promocode/"
    response = await make_post_request(url, query_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "discount_type": "fixed",
        "discount_value": 10.0,
        "final_amount": 90.0
    }


async def test_cancel_use_promocode(make_post_request, mock_purchase_service):
    mock_purchase_service.get_purchase.return_value = {"id": 1, "price": 100.0}
    mock_purchase_service.cancel_purchase.return_value = 100.0

    query_data = {"promocode": "TESTCODE", "purchase_id": 1}
    url = SERVICE_URL + "/api/v1/promocodes/cancel_use_promocode/"
    response = await make_post_request(url, query_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "discount_type": None,
        "discount_value": 0,
        "final_amount": 100.0
    }
