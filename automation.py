import time
from typing import Set, Dict, List
import config
from omnidim_client import OmniDimClient

import gspread
from google.oauth2.service_account import Credentials
import json
import logging
import re
from pathlib import Path


class Automation:
    """Main automation class for monitoring leads and dispatching calls via Google Sheets."""

    def __init__(self):
        """Initialize the automation with API client, Google Sheets client, and tracking."""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
        self.client = OmniDimClient(config.OMNIDIM_API_KEY)
        self.processed_leads: Set[str] = set()
        state_file = getattr(config, "PROCESSED_STATE_FILE", None) or "processed_leads.json"
        self._state_file = Path(state_file)

        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.readonly"]
        creds_path = Path(getattr(config, "CREDENTIALS_FILE", "credentials.json"))
        try:
            creds = Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
            self.gclient = gspread.authorize(creds)
            self.sheet_name = getattr(config, "SHEET_NAME", "Real Estate Database")
            self.worksheet = self.gclient.open(self.sheet_name).sheet1
        except Exception as e:
            logging.error(f"Failed to initialize Google Sheets client: {e}")
            raise

        self._load_state()

    def _load_state(self):
        if self._state_file.exists():
            try:
                with open(self._state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.processed_leads = set(data.get("processed", []))
                    logging.info(f"Loaded {len(self.processed_leads)} processed lead ids")
            except Exception:
                logging.warning("Could not read state file; starting fresh")
                self.processed_leads = set()

    def _save_state(self):
        try:
            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump({"processed": list(self.processed_leads)}, f)
        except Exception as e:
            logging.warning(f"Failed to save state file: {e}")

    def _normalize_phone(self, phone: str) -> str:
       
        if phone is None:
            return ""
        s = str(phone).strip()
        if s == "":
            return ""
        digits = re.sub(r"\D", "", s)
        return digits  

    def read_leads(self) -> List[Dict]:
        """
        Read all leads from the Google Sheet.

        Returns:
            List of lead dictionaries
        """
        rows = self.worksheet.get_all_records()
        return rows

    def get_new_leads(self) -> List[Dict]:
        """
        Filter leads to find only new ones that haven't been processed.

        Returns:
            List of new lead dictionaries
        """
        all_leads = self.read_leads()
        new_leads = []

        for lead in all_leads:
            lead_id = lead.get('lead_id', '') or lead.get('Timestamp', '') 
            if lead_id and lead_id not in self.processed_leads:
                new_leads.append(lead)
        
        return new_leads

    def process_lead(self, lead: Dict):
        """
        Process a single lead by dispatching a call.
        """
        lead_id = lead.get('lead_id', '') or lead.get('Timestamp', '')
        phone_number = self._normalize_phone(lead.get('Phone Number', ''))

        if not phone_number:
            logging.info(f"Lead {lead_id} has no valid phone number, skipping")
            if lead_id:
                self.processed_leads.add(lead_id)
                self._save_state()
            return

        logging.info(f"Processing lead {lead_id}: {lead.get('Name', 'Unknown')}")

        call_id = None
        for attempt in range(1, 4):
            try:
                call_id = self.client.dispatch_call(phone_number, lead)
                if call_id:
                    break
            except Exception as e:
                logging.warning(f"Dispatch attempt {attempt} failed for {lead_id}: {e}")
            time.sleep(2 * attempt)

        if call_id:
            logging.info(f"✓ Call dispatched for lead {lead_id}")
        else:
            logging.error(f"✗ Failed to dispatch call for lead {lead_id}")

        if lead_id:
            self.processed_leads.add(lead_id)
            self._save_state()

    def run(self):
        """Main automation loop - monitors Google Sheet and processes new leads."""
        print("Automation started. Monitoring Google Sheets for new leads...")
        print(f"Google Sheet: {self.sheet_name}")
        print(f"Poll interval: {config.POLL_INTERVAL} seconds\n")

        while True:
            try:
                new_leads = self.get_new_leads()

                if new_leads:
                    print(f"Found {len(new_leads)} new lead(s)")
                    for lead in new_leads:
                        self.process_lead(lead)
                        time.sleep(2)

                time.sleep(config.POLL_INTERVAL)

            except KeyboardInterrupt:
                print("\nAutomation stopped by user")
                break
            except Exception as e:
                print(f"Error in automation loop: {e}")
                time.sleep(config.POLL_INTERVAL)


if __name__ == "__main__":
    automation = Automation()
    automation.run()
