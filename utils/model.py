from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Order(BaseModel):
    Layout: Dict[str, str] = Field(default={"name": "Transport Job", "id": "3384000001562002"})
    Deal_Name: Optional[str] = None
    Customer_id: Optional[str] = None
    Customer_Name: Optional[str] = None
    Drop_off_Location: Optional[str] = None
    PickupLocation: Optional[str] = None
    Stage: Optional[str] = Field(default="Shop for Quotes")
    Order_Status: Optional[str] = Field(default="Quote Requested")
    Carrier_Payment_Status: Optional[str] = Field(default="Unpaid")
    Customer_Payment_Status: Optional[str] = Field(default="Unpaid")
    Name: Optional[str] = None
    Orders: Optional[List] = None
    special_instructon: Optional[str] = None
    Tax_Province: Optional[str] = None
    Pickup_City: Optional[str] = None
    Dropoff_City: Optional[str] = None
    Pickup_Province	: Optional[str] = None
    DealerAtDropoff: Optional[str] = None
    DealerAtPickup: Optional[str] = None
    ContactPickup: Optional[str] = None
    ContactDropoff: Optional[str] = None