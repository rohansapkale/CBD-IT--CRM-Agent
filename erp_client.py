import requests
import json
import re
import os
from dotenv import load_dotenv
from email_utils import send_email

# =========================
# CONFIG
# =========================
ERP_URL = "http://127.0.0.1:8000/api/resource"

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

# =========================
# CREATE LEAD
# =========================
def create_lead(data):
    url = f"{ERP_URL}/Lead"

    payload = {
        "first_name": data.get("name"),
        "email_id": data.get("email"),
        "mobile_no": data.get("phone"),
        "company_name": data.get("company"),
        "gender": data.get("gender"),
        "job_title": data.get("job_title"),
        "status": "Open"
    }

    payload = {k: v for k, v in payload.items() if v}

    res = requests.post(url, json=payload, headers=headers)
    print("📦 Lead Created:", res.text)

    return res.json()


# =========================
# FIND LEAD
# =========================
def find_lead(data):
    url = f"{ERP_URL}/Lead"

    search_fields = [
        ("email_id", data.get("email")),
        ("mobile_no", data.get("phone")),
        ("company_name", data.get("company")),
        ("lead_name", data.get("name")),
    ]

    for field, value in search_fields:
        if not value:
            continue

        filters = json.dumps([[field, "like", f"%{value}%"]])

        full_url = f'{url}?fields=["name","lead_name","company_name","status","email_id"]&filters={filters}'

        res = requests.get(full_url, headers=headers)
        leads = res.json().get("data", [])

        if leads:
            print("✅ Match Found:", leads[0])
            return leads[0]

    return None


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

    url = f"{ERP_URL}/Lead/{lead['name']}"
    payload = {"status": new_status}

    res = requests.put(url, json=payload, headers=headers)
    print("🔁 Status Updated:", res.text)


# =========================
# GET ITEM CODE
# =========================
def get_item_code(item_name):
    url = f"{ERP_URL}/Item"

    filters = json.dumps([["item_name", "=", item_name]])
    full_url = f'{url}?fields=["item_code","item_name"]&filters={filters}'

    res = requests.get(full_url, headers=headers)
    items = res.json().get("data", [])

    if items:
        return items[0]["item_code"]

    return None


# =========================
# CREATE QUOTATION
# =========================
def create_quotation(lead, item_code, qty, rate):

    url = f"{ERP_URL}/Quotation"

    payload = {
        "doctype": "Quotation",
        "quotation_to": "Lead",
        "party_name": lead["name"],
        "transaction_date": "2026-04-01",
        "valid_till": "2026-04-10",
        "items": [
            {
                "item_code": item_code,
                "qty": qty,
                "rate": rate
            }
        ]
    }

    print("🚀 FINAL PAYLOAD:", payload)

    res = requests.post(url, json=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("RAW:", res.text)

    response = res.json()

    # ✅ EMAIL TRIGGER (ONLY ON SUCCESS)
    if response.get("data"):
        quotation_name = response["data"]["name"]

        print("📄 Quotation Created:", quotation_name)

        pdf = get_quotation_pdf(quotation_name)

        if pdf and lead.get("email_id"):
            send_email(
            to_email=lead["email_id"],
            subject="Your Quotation",
            body=f"""
Hello {lead.get('lead_name')},

Please find attached your quotation.

Quotation ID: {quotation_name}

Thank you.
""",
            attachment=pdf,
            filename=f"{quotation_name}.pdf"
        )


# =========================
# 🔥 QUOTATION FLOW
# =========================
def handle_quotation_flow(text):

    match = re.search(r'share quotation to (.+)', text, re.IGNORECASE)

    if not match:
        print("❌ Could not extract company")
        return

    company = match.group(1).strip()
    print("📌 Searching for:", company)

    lead = find_lead({"company": company})

    if not lead:
        print("❌ Lead not found")
        return

    if lead.get("status") != "Quotation":
        print(f"⚠️ Lead status is '{lead.get('status')}'")
        print("👉 Update status to 'Quotation' first")
        return

    print("✅ Lead ready:", lead["name"])

    # PRODUCT MENU
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
        "6": "Tally Prime WhatsApp Renewal"
    }

    item_name = product_map.get(choice)

    if not item_name:
        print("❌ Invalid choice")
        return

    item_code = get_item_code(item_name)

    if not item_code:
        print("❌ Item not found in ERP:", item_name)
        return

    try:
        qty = int(input("Enter Quantity: "))
        rate = float(input("Enter Rate: "))
    except ValueError:
        print("❌ Invalid input")
        return

    create_quotation(lead, item_code, qty, rate)

def get_quotation_pdf(quotation_name):
    url = "http://127.0.0.1:8000/api/method/frappe.utils.print_format.download_pdf"

    params = {
        "doctype": "Quotation",
        "name": quotation_name,
        "format": "Standard"
    }

    res = requests.get(url, params=params, headers=headers)

    if res.status_code == 200:
        return res.content  # binary PDF
    else:
        print("❌ Failed to fetch PDF:", res.text)
        return None