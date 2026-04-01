from erp_client import create_lead, update_lead_status, handle_quotation_flow
from extractor import extract_data
from llm_extractor import extract_with_llm

try:
    while True:
        text = input("\nEnter command: ")
        text_lower = text.lower()

        # -------------------------
        # 🔥 PRIORITY 1: QUOTATION
        # -------------------------
        if "share quotation" in text_lower:
            handle_quotation_flow(text)

        else:
            # -------------------------
            # STEP 1: EXTRACT
            # -------------------------
            regex_data = extract_data(text)
            print("Regex:", regex_data)

            llm_data = extract_with_llm(text)
            print("LLM:", llm_data)

            # -------------------------
            # STEP 2: MERGE
            # -------------------------
            final_data = {}

            for key in ["name", "email", "company", "phone", "gender", "job_title"]:
                val1 = regex_data.get(key)
                val2 = llm_data.get(key)

                final_data[key] = val1 if val1 else (val2 if val2 else None)

            print("Final:", final_data)

            # -------------------------
            # 🔁 UPDATE FLOW
            # -------------------------
            if "update" in text_lower or "status" in text_lower or "change" in text_lower:

                status = None
                for s in [
                    "Open", "Lead", "Quotation", "Opportunity",
                    "Lost Quotation", "Do Not Contact",
                    "Interested", "Converted", "Replied"
                ]:
                    if s.lower() in text_lower:
                        status = s
                        break

                if not status:
                    print("❌ No valid status found")
                else:
                    print("🔁 Updating status to:", status)
                    update_lead_status(final_data, status)

            # -------------------------
            # 🚀 CREATE FLOW
            # -------------------------
            else:
                print("🚀 Creating lead...")
                create_lead(final_data)

# ✅ Exit using CTRL + C
except KeyboardInterrupt:
    print("\n👋 Exiting CRM Agent... Bye!")
