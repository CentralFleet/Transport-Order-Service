# CF - Transport Orders Service

## Overview
The Transport Orders Service is a scalable solution built using **Serverless App** and integrates with **Zoho CRM** to streamline the management of transport orders. The service enables seamless order creation, updates, and file management while maintaining robust database support for persistence and tracking.

## Features
- **Order Creation**:
  - Creates transport orders in the SQL database and Zoho CRM.
  - Associates vehicles with transport orders, including their pickup and drop-off details.
  - Supports the attachment of release forms to Zoho CRM records.

- **Order Updates**:
  - Updates transport order details in Zoho CRM and the SQL database.
  - Handles updates for order status, estimated times, pricing, and more.

- **File Management**:
  - Downloads and attaches release forms to Zoho CRM records (e.g., Deals and Vehicles modules).
  - Cleans up temporary files after processing.

- **Slack Notifications**:
  - Sends Slack notifications for new transport orders with relevant details and a link to the Zoho CRM record.

## Endpoints
### `GET /ping`
**Description**: A health check endpoint to verify the service is up and running.  
**Response**:  
```json
{
  "message": "Service is up"
}
```
### `POST /order?action=create`
**Description**: Creates a new transport order in both the database and Zoho CRM.  
**Request Body**:  
```json
{
  "Customer_id": "12345",
  "Customer_name": "John Doe",
  "Dropoff_Location": "Toronto, ON",
  "Pickup_Location": "Vancouver, BC",
  "Special_Instruction": "Handle with care",
  "Pickup_City": "Vancouver",
  "Dropoff_City": "Toronto",
  "Pickup_Province":"British Columbia",
  "Dropoff_Province":"Ontario",
  "DealerAtDropoff": "Dealer A",
  "DealerAtPickup": "Dealer B",
  "ContactDropoff": "+123-454-4535",
  "ContactPickup": "+123-454-4535",
  "Vehicles": [
    {
      "Make": "Toyota",
      "Model": "Camry",
      "Trim": "SE",
      "VIN": "1HGBH41JXMN109186",
      "ReleaseForm": "https://example.com/release_form.pdf"
    }
  ]
}

```
**Response**:

```json
{
    "status": "sucess",
    "code": 201,
    "Deal_Name": "#10008",
    "zoho_order_id": "3384000001971023",
    "vehicles": [
        {
            "Year": "2020",
            "Make": "Toyota",
            "VIN": "1HGCR2F31HA805514",
            "Model": "Camry",
            "Trim": "4dr Sdn AWD",
            "ReleaseForm": "https://icseindia.org/document/sample.pdf",
            "Mileage": "35454",
            "Name": "Toyota Camry 4dr Sdn AWD - 1HGCR2F31HA805514",
            "Order_Status": "Pending",
            "Deal_ID": "3384000001971023",
            "Pickup_Location": "8 Ott Dr, Unit 101 Huntsville, ON P1H 0A2, CA",
            "Dropoff_Location": "3500 A. Jean-Noël-Lavoie, Laval, QC H7T 2H6",
            "Vehicle_ID": "3384000001972003"
        },
    ]
}
```

### `POST /order?action=update`
**Description**: Updates a transport order in Zoho CRM.  
**Request Body**:  
```json
{
  "DealID": "338400000123456789",
  "Status": "Delivered",
  "EstimatedDropoffTime": "2025-01-20T14:00:00Z"
}

```

### `POST /update-sqlorder`
**Description**: Updates a transport order in the Reference database.
**Request Body**:
```json

​{
  "DealID": "338400000123456789",
  "Status": "Delivered",
  "EstimatedDropoffTime": "2025-01-20T14:00:00Z"
  
}

```


## 🛠️ Contributing Guide  

Thank you for considering contributing to this project! Follow these steps to get started:  

### 🚀 Steps to Contribute  

1. **Fork the Repository**  
   Click the **Fork** button at the top right of this repository to create your own copy.  

2. **Clone Your Fork**  
   ```sh
   git clone https://github.com/CentralFleet/Transport-Order-Service.git
   cd Transport-Order-Service
   ```
3. **Create a New Branch**
   ```sh
   git checkout -b your-branch-name
   ```
4. **Make Your Changes**
    Make your changes and commit them to your local branch

5. **Push Your Changes**
    ```sh
    git push origin your-branch-name
    ```

6. **Create a Pull Request**
    Navigate to your forked repository on GitHub and create a new pull request.

