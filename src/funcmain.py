# src/funcmain.py
from utils.helpers import *
from utils.model import *

import azure.functions as func
import json
import os
from src.dbConnector import *
from sqlalchemy import and_, text, func as sqlfunc
from sqlalchemy.exc import IntegrityError
from pyzohocrm import ZohoApi, TokenManager
from dotenv import load_dotenv
load_dotenv()
logger = get_logger(__name__)


TEMP_DIR = "/tmp"
FILE_PREFIX = "RF-"
TOKEN_INSTANCE =  TokenManager(
                                domain_name="Canada",
                                refresh_token=os.getenv("REFRESH_TOKEN"),
                                client_id=os.getenv("CLIENT_ZOHO_ID"),
                                client_secret=os.getenv("CLIENT_ZOHO_SECRET"),
                                grant_type="refresh_token",
                                token_dir=TEMP_DIR
                                )

ZOHO_API = ZohoApi(base_url="https://www.zohoapis.ca/crm/v2")

class TransportOrders:
    def __init__(self):
        pass

    def parse_release_forms(self, vehicles):
        try:
            release_forms = [manage_prv(v["ReleaseForm"]) for v in vehicles if v.get('ReleaseForm') not in ['null', None, '']]
            logger.info(f"Release Forms: {release_forms}")
            return release_forms
        except Exception as e:
            logger.error(f"Error parsing release forms: {e}")
            return []

    def create_order_db(self, session, body):
        try:
            order_obj = OrdersDB(
                CustomerID=body.get("Customer_id", ""),
                CustomerName=body.get("Customer_name", ""),
                DropoffLocation=body.get("Dropoff_Location", ""),
                PickupLocation=body.get("Pickup_Location", ""),
                Status="Pending",
                DearlerAtPickup = body.get("DealerAtPickup", ""),
                DearlerAtDropoff = body.get("DealerAtDropoff", ""),
                ContactDropoff = body.get("ContactDropoff", ""),
                ContactPickup = body.get("ContactPickup", ""),

            )
            session.add(order_obj)
            session.flush()  # Fetch the generated OrderID
            logger.info(f"Created Order in DB with ID: {order_obj.OrderID}")
            return order_obj
        except Exception as e:
            logger.error(f"Error creating order in DB: {e}")
            session.rollback()
            return None

    def create_order_zoho(self, order_obj, body, token):
        try:
            order_data = Order(
                Deal_Name=f"#{order_obj.OrderID}",
                Customer_id=body.get("Customer_id", ""),
                Customer_Name=body.get("Customer_name", ""),
                Drop_off_Location=body.get("Dropoff_Location", ""),
                PickupLocation=body.get("Pickup_Location", ""),
                special_instructon=body.get("Special_Instruction", ""),
                Tax_Province=body.get("Pickup_Province", "").replace("é", "e"),
                Dropoff_Province=body.get("Dropoff_Province", "").replace("é", "e"),
                Pickup_City = body.get("Pickup_City", ""),
                Dropoff_City= body.get("Dropoff_City", ""),
                DealerAtDropoff=body.get("DealerAtDropoff", ""),
                DealerAtPickup=body.get("DealerAtPickup", ""),
                ContactDropoff=body.get("ContactDropoff", ""),
                ContactPickup=body.get("ContactPickup", ""),
                
            )
            response = ZOHO_API.create_record(moduleName="Deals", data={"data": [order_data.dict()]}, token=token)
            deal_id = response.json()['data'][0]['details']['id']
            logger.info(f"Zoho Order created with ID: {deal_id}")
            return deal_id
        except Exception as e:
            logger.error(f"Error creating order in Zoho CRM: {e}")
            return None
        
    def create_vehicles_in_zoho(self, vehicles, deal_id, token,order_obj):
        try:
            layout_info = {
                "name": "Transport Vehicles",
                "id": "3384000001943151"
            }

            for vehicle in vehicles:
                    # Ensure 'Layout' exists and add/update its keys
                    vehicle['Layout'] = vehicle.get('Layout', {})
                    vehicle['Layout'].update(layout_info)
                    vehicle['Name'] = f"{vehicle['Make']} {vehicle['Model']} {vehicle['Trim']} - {vehicle['VIN']}"
                    vehicle['Source'] = "Transport Request"
                    vehicle['Order_Status'] = "Pending"
                    vehicle['Deal_ID'] = deal_id
                    vehicle['Pickup_Location'] = order_obj.PickupLocation
                    vehicle['Dropoff_Location'] = order_obj.DropoffLocation
            logger.info(f"Vehicles: {vehicles}")
            response = ZOHO_API.create_record(moduleName="Vehicles", data={"data": vehicles}, token=token)

            logger.info(f"Batch Vehicle response: {response.json()}")
            if response.json().get("data"):
                for vehicle, record in zip(vehicles, response.json()["data"]):
                    vehicle["Vehicle_Record_ID"] = record.get("details", {}).get("id")  

            return response.json()
        except Exception as e:
            logger.error(f"Error creating vehicles in Zoho: {e}")
            return None

    def attach_files(self, deal_id, file_urls, token):
        for url in file_urls:
            try:
                
                original_filename = os.path.basename(url)
                prefixed_filename = FILE_PREFIX + original_filename  # Add the prefix
                local_file_path = os.path.join(TEMP_DIR, prefixed_filename)
                download_file(url, local_file_path)
                response = ZOHO_API.attach_file(moduleName="Deals", record_id=deal_id, file_path=local_file_path, token=token)
                logger.info(f"File attached response: {response.json()}")
                os.remove(local_file_path)
            except Exception as e:
                logger.warning(f"Error attaching files in Zoho: {e}")

    async def _create_order(self, body: json) -> dict:
        try:
            token = TOKEN_INSTANCE.get_access_token()
            vehicles = body.get("Vehicles", [])
            # release_forms = self.parse_release_forms(vehicles)
            
            with DatabaseConnection(connection_string=os.getenv("SQL_CONN_STR")) as session:
                session.begin()
                order_obj = self.create_order_db(session, body)
                if not order_obj:
                    return {"error": "DB order creation failed", "message": "Error creating order", "code": 500}
                
                deal_id = self.create_order_zoho(order_obj, body, token)
                if not deal_id:
                    session.rollback()
                    return {"error": "Zoho order creation failed", "message": "Error creating order", "code": 500}

                try:
                    release_forms = body.get("ReleaseForms").split(",")
                    self.attach_files(deal_id, release_forms, token)
                except Exception as e:
                    logger.warning(f"Error attaching files in Zoho: {e}")
                vehicle_response = self.create_vehicles_in_zoho(vehicles, deal_id, token,order_obj)
                logger.info(f"Vehicle batch response: {vehicle_response}")
                order_obj.TransportRequestID = deal_id
                session.commit()
                logger.info("Order successfully created and committed to DB")

                slack_msg = f"""🚚 *New Transport Request* \n - Order ID: `{order_obj.OrderID}` \n - Vehicles: `{len(vehicles)}` \n - Pickup: `{order_obj.PickupLocation}` \n - Drop-off: `{order_obj.DropoffLocation}` \n <https://crm.zohocloud.ca/crm/org110000402423/tab/Potentials/{deal_id}|View Order Details>"""
                send_message_to_channel(os.getenv("BOT_TOKEN"), os.getenv("TRANSPORT_CHANNEL_ID"), slack_msg)
                
                return {
                "status": "success",
                "code": 201,
                "Deal_Name": f"#{order_obj.OrderID}",
                "zoho_order_id": deal_id,
                "vehicles": vehicles
            }
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {"error": str(e), "message": "Error creating order", "code": 500}

    async def _update_sql_order(self, body: dict):
        try:
            with DatabaseConnection(connection_string=os.getenv("SQL_CONN_STR")) as session:
                query = session.query(OrdersDB).filter_by(TransportRequestID=body.get("DealID", "")).first()
                if not query:
                    logger.warning("No record found with given primary key values")
                    return {"status": "error", "message": "Record not found"}
                
                updatable_fields = [
                    "Status", "EstimatedDropoffTime", "EstimatedPickupTime", "CarrierID", "CarrierName", "JobPrice", "CarrierCost", "ActualDeliveryTime", "ActualPickupTime"
                ]
                for field in updatable_fields:
                    if field in body and body[field] is not None:
                        value = body[field]
                        if value == '':
                            setattr(query, field, None)
                        else:
                            setattr(query, field, value)
                session.commit()
                return {"status": "success", "message": "Record updated successfully"}
        except Exception as e:
            logger.error(f"Error updating SQL order: {e}")
            return {"error": str(e), "message": "Error Updating Order", "code": 500}

    async def _update_order(self, body: json) -> dict:
        try:
            token = TOKEN_INSTANCE.get_access_token()
            body_filtered = body.copy()  # Ensure we don't modify the original data
            body_filtered.pop("DealID", None)  # Remove DealID if it exists
            
            return ZohoApi.update_record(moduleName="Deals", id=body.get("DealID", ""), data=body_filtered, token=token)
        except Exception as e:
            logger.error(f"Error updating order in Zoho: {e}")
            return {"error": str(e)}
