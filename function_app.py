# function_app.py
import azure.functions as func
from src.funcmain import *
from typing import Dict, Any
import json

Orderhandler = TransportOrders()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="ping", methods=["GET", "POST"])
async def ping(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logger.info(f"Request received from {req.url}")
        logger.info("Ping request received.")
        return func.HttpResponse("Service is up", status_code=200)
    except Exception as e:
        logger.error(f"Error in ping request: {str(e)}")
        return func.HttpResponse("Internal server error", status_code=500)


@app.route(route="order", methods=["POST"])
async def order(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logger.info(f"Request received from {req.url}")
        body: Dict[str, Any] = req.get_json()  # body is expected to be a dictionary
        logger.info(f"body : {body}")

        action = req.params.get("action")
        if action == "create":
            response = await Orderhandler._create_order(body)
            logger.info(f"Func app :{response}")
            if response["code"] == 201:
                return func.HttpResponse(json.dumps(response), status_code=201)
            else:
                return func.HttpResponse(json.dumps(response), status_code=500)

        elif action == "update":
            response = await Orderhandler._update_order(body)
            if response["code"] == 200:
                return func.HttpResponse(json.dumps(response), status_code=200)
            else:
                return func.HttpResponse(json.dumps(response), status_code=500)

        else:
            return func.HttpResponse("Invalid request", status_code=400)

    except Exception as e:
        logger.error(f"Error processing order request: {str(e)}")
        return func.HttpResponse("Internal server error", status_code=500)


@app.route(route="update-sqlorder", methods=["POST"])
async def update_sqlorder(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logger.info(f"Request received from {req.url}")

        body: Dict[str, Any] = req.get_json()  # body is expected to be a dictionary
        logger.info(f"body : {body}")

        response = await Orderhandler._update_sql_order(body)
        return func.HttpResponse(json.dumps(body), status_code=200)

    except Exception as e:
        logger.error(f"Error processing SQL order request: {str(e)}")
        return func.HttpResponse("Internal server error", status_code=500)
