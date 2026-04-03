from erp_client import create_lead, update_lead_status, handle_quotation_flow
from extractor import extract_data
from llm_extractor import extract_with_llm

def detect_intent(text):
    text = text.lower()

    if "share quotation" in text:
        return "quotation"

    if "update" in text or "status" in text or "change" in text:
        return "update"

    if "create" in text or "add" in text or "new lead" in text:
        return "create"

    return "unknown"


def extract_final_data(text):
    regex_data = extract_data(text)
    llm_data = extract_with_llm(text)

    print("🔍 Regex:", regex_data)
    print("🤖 LLM:", llm_data)

    final_data = {}

    for key in ["name", "email", "company", "phone", "gender", "job_title"]:
        val1 = regex_data.get(key)
        val2 = llm_data.get(key)

        final_data[key] = val1 if val1 else (val2 if val2 else None)

    print("📦 Final:", final_data)
    return final_data


def handle_update(text, data):
    VALID_STATUS = [
        "Open", "Lead", "Quotation", "Opportunity",
        "Lost Quotation", "Do Not Contact",
        "Interested", "Converted", "Replied"
    ]

    status = None
    for s in VALID_STATUS:
        if s.lower() in text.lower():
            status = s
            break

    if not status:
        print("❌ No valid status found")
        return

    print("🔁 Updating status to:", status)
    update_lead_status(data, status)


def agent():
    print("\n🤖 CRM AI Agent Ready (TinyLLaMA Powered)")
    print("Type 'exit' or press Ctrl+C to quit\n")

    while True:
        try:
            text = input("🧠 You: ").strip()

            if not text:
                continue

            if text.lower() in ["exit", "quit"]:
                print("👋 Exiting agent...")
                break

            intent = detect_intent(text)

            # -------------------------
            # 🔥 QUOTATION FLOW
            # -------------------------
            if intent == "quotation":
                handle_quotation_flow(text)

            # -------------------------
            # 🔁 UPDATE FLOW
            # -------------------------
            elif intent == "update":
                data = extract_final_data(text)
                handle_update(text, data)

            # -------------------------
            # 🚀 CREATE FLOW
            # -------------------------
            elif intent == "create":
                data = extract_final_data(text)
                print("🚀 Creating lead...")
                create_lead(data)

            else:
                print("🤖 I didn’t understand. Try,Something like this:")
                print("- Create lead for Rohan from ABC company")
                print("- Update ABC company to Quotation")
                print("- Share quotation to ABC company")

        except KeyboardInterrupt:
            print("\n👋 Agent stopped (Ctrl+C)")
            break

        except Exception as e:
            print("❌ Error:", str(e))


if __name__ == "__main__":
    agent()
