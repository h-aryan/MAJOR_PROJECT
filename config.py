import os
from dotenv import load_dotenv

load_dotenv()

OMNIDIM_API_KEY = os.getenv('OMNIDIM_API_KEY', '')
AGENT_ID = os.getenv('AGENT_ID', '')

INPUT_CSV_PATH = os.getenv('INPUT_CSV_PATH', 'leads_input.csv')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '5'))

print(f"OMNIDIM_API_KEY: {OMNIDIM_API_KEY}")
print(f"AGENT_ID: {AGENT_ID}")
print(f"POLL_INTERVAL: {POLL_INTERVAL}")