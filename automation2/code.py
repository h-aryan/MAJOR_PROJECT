import gspread
import requests
import time
import logging
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

class OmniDimClient:
    def __init__(self, api_key: str, agent_id: int):
        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = "https://backend.omnidim.io/api/v1"
    
    def dispatch_call(self, phone_number: str, lead_data: Dict) -> str:
        call_context = {
            "customer_name": lead_data.get('Column 2', 'Unknown'),
            "email": lead_data.get('Column 3', 'N/A')
        }
        payload = {
            "agent_id": self.agent_id,
            "to_number": phone_number,
            "call_context": call_context
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            logging.info(f"Dispatching call with payload: {payload}")
            response = requests.post(f"{self.base_url}/calls/dispatch", json=payload, headers=headers)
            response.raise_for_status()

            logging.info(f"API Response Status Code: {response.status_code}")
            logging.info(f"API Response Body: {response.text}")

            if response.status_code != 200:
                logging.error(f"API returned an error: {response.json().get('error', 'Unknown error')}")
                return ""

            return response.json().get("call_id", "")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error dispatching call: {e}")
            return ""

class GoogleSheets:
    def __init__(self, creds_file: str, sheet_name: str):
        self.creds_file = creds_file
        self.sheet_name = sheet_name
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.readonly"]
        self.creds = Credentials.from_service_account_file(creds_file, scopes=self.SCOPES)
        
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        
        self.gclient = gspread.authorize(self.creds)
        self.sheet = self.gclient.open(self.sheet_name).sheet1

    def clear_sheet(self):
        try:
            self.sheet.clear()
            logging.info("Sheet data cleared.")
        except Exception as e:
            logging.error(f"Error clearing sheet: {e}")

    def get_new_leads(self) -> List[Dict]:
        rows = self.sheet.get_all_records()
        new_leads = [row for row in rows if row.get("Processed") != "Yes"]
        logging.info(f"Found {len(new_leads)} new leads to process.")
        return new_leads

    def mark_as_processed(self, lead_id: str):
        try:
            cell = self.sheet.find(lead_id)
            self.sheet.update_cell(cell.row, cell.col + 1, "Yes")
            logging.info(f"Marked lead {lead_id} as processed.")
        except Exception as e:
            logging.error(f"Error marking lead {lead_id} as processed: {e}")

def main():
    api_key = "xlP31UxwqhRwc6gBqKbtABtcQaH65Fmfc4urA1Y59I0"
    agent_id = "64073"
    creds_file = "credentials.json"
    sheet_name = "Enquiry"

    omnidim_client = OmniDimClient(api_key, agent_id)
    google_sheets = GoogleSheets(creds_file, sheet_name)

    google_sheets.clear_sheet()

    while True:
        leads = google_sheets.get_new_leads()
        for lead in leads:
            phone_number = lead.get('Column 4', '')
            lead_id = lead.get('Lead ID', '')
            
            if phone_number:
                phone_number = str(phone_number) 
                if not phone_number.startswith('+'):
                    phone_number = '+' + phone_number
                
                logging.info(f"Processing lead: {lead['Column 2']} with phone number {phone_number}")
                call_id = omnidim_client.dispatch_call(phone_number, lead)
                if call_id:
                    logging.info(f"Call dispatched successfully. Call ID: {call_id}")
                    google_sheets.mark_as_processed(lead_id)
                else:
                    logging.error(f"Failed to dispatch call for lead {lead_id}")
            time.sleep(2)
        time.sleep(5)

if __name__ == "__main__":
    main()
