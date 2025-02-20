import pytest
from unittest.mock import patch, MagicMock
from src.funcmain import TransportOrders
import azure.functions as func
import os
import json
@pytest.fixture
def transport_orders():
    return TransportOrders()

@pytest.fixture
def mock_request():
    def _mock_request(body):
        req = MagicMock(spec=func.HttpRequest)
        req.get_json.return_value = body
        return req
    return _mock_request

@pytest.mark.asyncio
@patch("src.funcmain.TOKEN_INSTANCE.get_access_token")
@patch("src.funcmain.ZOHO_API.create_record")
@patch("src.dbConnector.DatabaseConnection")
@patch("src.funcmain.send_message_to_channel")
async def test_create_order(mock_slack, mock_db, mock_zoho, mock_token, transport_orders, mock_request):
    mock_token.return_value = "fake_token"
    mock_zoho.return_value.json.return_value = {"data": [{"details": {"id": 98765}}]}
    mock_slack.return_value = None
    mock_session = MagicMock()
    mock_db.return_value.__enter__.return_value = mock_session
    mock_order = MagicMock()
    mock_session.add.return_value = None
    mock_session.flush.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_order
    body = {
        "Customer_id": "12345",
        "Customer_name": "John Doe",
        "Dropoff_Location": "Toronto",
        "Pickup_Location": "Vancouver",
        "Vehicles": [],
        "ReleaseForms": "form1.pdf,form2.pdf"
    }
    result = await transport_orders._create_order(body)
    assert result["status"] == "success"
    assert result["zoho_order_id"] == 98765