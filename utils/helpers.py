# utils/helpers.py
import re
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests

logger = logging.getLogger(__name__)

# Function to configure logging
def get_logger(name):
    # Create a logger
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, don't add more (this avoids duplicate logs)
    if not logger.hasHandlers():
        # Set logging level
        logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add the console handler to the logger
        logger.addHandler(console_handler)
    
    return logger

def send_message_to_channel(bot_token, channel_id, message):
    client = WebClient(token=bot_token)

    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=message,
            unfurl_links=False,  # Disable link previews
    unfurl_media=False 
        )
        print(f"Message successfully sent to channel {channel_id} on Slack")
    except SlackApiError as e:
        print(f"Error sending Message to slack: {e}")


def manage_prv(url):
    if url.startswith("//"):
        url = "https:" + url
    else:
        return url

    return url

def extract_tax_province(province_address):
    province_address = province_address.upper()  # Convert to lowercase for flexibility
    province_map = {
        "AB": "Alberta",
        "BC": "British Columbia",
        "MB": "Manitoba",
        "NB": "New Brunswick",
        "NL": "Newfoundland and Labrador",
        "NS": "Nova Scotia",
        "ON": "Ontario",
        "PE": "Prince Edward Island",
        "QC": "Quebec",
        "SK": "Saskatchewan",
        "NT": "Northwest Territories",
        "NU": "Nunavut",
        "YT": "Yukon"
    }
    # First check for full province name (in case it's already present in the address)
    for code, abbreviation in province_map.items():
        if abbreviation.upper() in province_address:
            return abbreviation.capitalize()  # Return the full name as a proper noun (capitalized)

    # Then check for province abbreviation (2-letter code)
    match = re.search(r"\b([A-Z]{2})\b", province_address)  # Regex looks for 2-letter province code
    
    if match:
        province_abbreviation = match.group(1)
        tax_province = province_map.get(province_abbreviation, "Unknown Province")
        return tax_province.capitalize()  # Return the province name corresponding to the abbreviation
    else:
        return "Unknown Province"


def download_file(url: str, destination_path: str):
    """Download a file synchronously from a public URL."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(destination_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logger.info(f"Downloaded file to: {destination_path}")
    else:
        raise Exception(f"Failed to download file from {url}: {response.status_code}")