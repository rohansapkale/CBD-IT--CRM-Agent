import requests
import json
import re
import os
from dotenv import load_dotenv

ERP_URL = "http://127.0.0.1:8000/api/resource/Lead"

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

headers = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}

VALID_STATUS = [
    "Open", "Lead", "Quotation", "Opportunity",
    "Lost Quotation", "Do Not Contact",
    "Interested", "Converted", "Replied"
]
def create_customer_from_lead(lead):

    url = "http://127.0.0.1:8000/api/resource/Customer"

    customer_name = (
        lead.get("company_name")
        or lead.get("lead_name")
        or "Default Customer"
    )

    payload = {
        "customer_name": customer_name,
        "customer_type": "Company"
    }

    print("👤 Creating Customer:", payload)

    res = requests.post(url, json=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("RAW:", res.text)

    data = res.json()

    return data.get("data", {}).get("name")


# =========================
# CREATE LEAD
# =========================
def create_lead(data):

    payload = {
        "first_name": data.get("name"),
        "email_id": data.get("email"),
        "mobile_no": data.get("phone"),
        "company_name": data.get("company"),
        "gender": data.get("gender"),
        "job_title": data.get("job_title"),
        "type": data.get("lead_type"),
        "request_type": data.get("request_type"),
        "status": "Open"
    }

    payload = {k: v for k, v in payload.items() if v}

    print("📦 Payload:", payload)

    res = requests.post(ERP_URL, json=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("RAW:", res.text)

    return res.json()
#==========================
def create_quotation(lead, item_name):

    # 🔥 STEP 1: Create customer
    customer = create_customer_from_lead(lead)

    if not customer:
        print("❌ Customer creation failed")
        return

    # 🔥 STEP 2: Create quotation
    url = "http://127.0.0.1:8000/api/resource/Quotation"

    payload = {
        "quotation_to": "Customer",   # ✅ FIXED
        "party_name": customer,       # ✅ FIXED

        "items": [
            {
                "item_code": item_name,
                "qty": 1,
                "rate": 1000
            }
        ]
    }

    print("📦 Creating Quotation:", payload)

    res = requests.post(url, json=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("RAW:", res.text)

    return res.json()
# =========================
# UPDATE STATUS
# =========================
def update_lead_status(data, new_status):

    if new_status not in VALID_STATUS:
        print("❌ Invalid status")
        return

    lead = find_lead(data)

    if not lead:
        print("❌ No lead found")
        return

    lead_id = lead["name"]

    print("🎯 Updating:", lead_id)

    url = f"{ERP_URL}/{lead_id}"

    payload = {"status": new_status}

    res = requests.put(url, json=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("RAW:", res.text)


# =========================
# 🔥 QUOTATION FLOW
# =========================
def handle_quotation_flow(text):
    import re

    match = re.search(r'share quotation to (.+)', text, re.IGNORECASE)

    if not match:
        print("❌ Could not extract company")
        return

    company = match.group(1).strip()

    print("📌 Searching for:", company)

    lead = find_lead(company)

    if not lead:
        print("❌ Lead not found")
        return

    if lead.get("status") != "Quotation":
        print(f"⚠️ Lead found but status is '{lead.get('status')}'")
        print("👉 Please update status to 'Quotation' first")
        return

    print("✅ Lead ready for quotation:", lead["name"])

    # -------------------------
    # PRODUCT MENU
    # -------------------------
    print("\n📦 Select Product:")
    print("1. Tally Prime Single User")
    print("2. Tally Prime Multi User")
    print("3. Tally Prime Single User Renewal")
    print("4. Tally Prime Multi User Renewal")
    print("5. Tally Prime Whatsapp Subscription")
    print("6. Tally Prime WhatsApp Renewal")

    choice = input("Enter choice (1-6): ").strip()

    product_map = {
        "1": "Tally Prime Single User",
        "2": "Tally Prime Multi User",
        "3": "Tally Prime Single User Renewal",
        "4": "Tally Prime Multi User Renewal",
        "5": "Tally Prime Whatsapp Subscription",
        "6": "Tally Prime Whatsapp Renewal"
    }

    item_name = product_map.get(choice)

    if not item_name:
        print("❌ Invalid choice")
        return

    create_quotation(lead, item_name)


def create_quotation(lead, item_name):
    url = "http://127.0.0.1:8000/api/resource/Quotation"

    payload = {
        "quotation_to": "Customer",
        "party_name": "Test Customer",

        "items": [
            {
                "item_code": item_name,
                "qty": 1,
                "rate": 1000
            }
        ]
    }

    print("📦 Creating Quotation Payload:", payload)

    res = requests.post(url, json=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("RAW:", res.text)

    return res.json()
# FIND LEAD
# =========================
def find_lead(data):

    search_fields = [
        ("email_id", data.get("email")),
        ("mobile_no", data.get("phone")),
        ("company_name", data.get("company")),
        ("lead_name", data.get("name")),
        ("title", data.get("company")),
    ]

    for field, value in search_fields:

        if not value:
            continue

        filters = [[field, "like", f"%{value}%"]]

        filters_json = json.dumps(filters)

        url = f"{ERP_URL}?fields=[\"name\",\"lead_name\",\"company_name\",\"status\",\"email_id\",\"mobile_no\"]&filters={filters_json}"

        print("🔍 Trying:", url)

        res = requests.get(url, headers=headers)
        data_res = res.json()

        leads = data_res.get("data", [])

        if leads:
            print("✅ Match Found:", leads[0])
            return leads[0]

    return None
# =========================
# MAP ITEM
# =========================
def map_item(choice):

    items = {
        "1": "SU",
        "2": "MU",
        "3": "SU TSS",
        "4": "MU TSS",
        "5": "Tally WhatsApp",
        "6": "Tally WhatsApp Renewal"
    }

    return items.get(choice)


# =========================
# CREATE CUSTOMER
# =========================
def create_customer(lead):

    url = "http://127.0.0.1:8000/api/resource/Customer"

    payload = {
        "customer_name": lead["lead_name"],
        "customer_type": "Company"
    }

    res = requests.post(url, json=payload, headers=headers)

    return res.json().get("data", {}).get("name")


# =========================
# CREATE QUOTATION
# =========================
def create_quotation(customer, item):

    url = "http://127.0.0.1:8000/api/resource/Quotation"

    payload = {
        "customer": customer,
        "items": [
            {
                "item_name": item,
                "qty": 1,
                "rate": 1000
            }
        ]
    }

    res = requests.post(url, json=payload, headers=headers)

    print("📄 Quotation Created")
    print(res.text)
