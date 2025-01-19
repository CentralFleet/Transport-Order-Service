# function_app.py
import azure.functions as func
from src.funcmain import *

Orderhandler = TransportOrders()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="ping", methods=["GET", "POST"])
async def ping(req: func.HttpRequest) -> func.HttpResponse:
    logger.info(f"Request received from {req.url}")
    logger.info("Ping request received.")
    return func.HttpResponse("Service is up", status_code=200)


@app.route(route="order", methods=["POST"])
async def order(req: func.HttpRequest) -> func.HttpResponse:
    logger.info(f"Request received from {req.url}")
    body = req.get_json()
    logger.info(f"body : {body}")

    if req.params.get("action") == "create":

        try:
            response = await Orderhandler._create_order(body)
            logger.info(f"Func app :{response}")
            return func.HttpResponse(json.dumps(response), status_code=200)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return func.HttpResponse("Internal server error", status_code=500)

    elif req.params.get("action") == "update":
        try:
            response = await Orderhandler._update_order(body)

            return func.HttpResponse(json.dumps(response), status_code=200)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return func.HttpResponse("Internal server error", status_code=500)

    else:
        return func.HttpResponse("Invalid request", status_code=400)


@app.route(route="update-sqlorder", methods=["POST"])
async def update_sqlorder(req: func.HttpRequest) -> func.HttpResponse:

    logger.info(f"Request received from {req.url}")

    body = req.get_json()
    logger.info(f"body : {body}")

    response = await Orderhandler._update_sql_order(body)

    return func.HttpResponse(json.dumps(body), status_code=200)
