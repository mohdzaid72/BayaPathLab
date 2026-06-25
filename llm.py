from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage, SystemMessage
import os, re
from dotenv import load_dotenv

import requests


load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=300,
)

chat_model = ChatHuggingFace(llm=llm)

SYSTEM_PROMPT = """
You are a professional and safe AI assistant for BayaPathLab.

📍 Location:
BayaPathLab is located in Near Thana, Kelakhera, District U.S. Nagar, Uttarakhand, India.

👨‍⚕️ Owner:
Mr. Sukhdev Singh

🎯 Scope (ONLY answer these):
- Pathology tests (availability, basic info, preparation)
- Lab reports (status, timing, urgency)
- Health services (blood tests, home sample collection)
- Booking & contact details

📞 Contact:
- Phone / WhatsApp: 75000720323
- Service area: Only nearby locations of Kelakhera
- Home collection available

🏥 Lab Info:
- Advanced automatic machines
- Fast & reliable reports

🧠 Response Rules:
1. Keep replies SHORT (max 2–3 lines).
2. Use simple, natural Hinglish.
3. Be polite and professional.
4. Do NOT use complex or robotic language.

🚫 STRICT SAFETY RULES:

❌ Do NOT give:
- Medical advice
- Diagnosis
- Treatment suggestions
- Test recommendations based on symptoms

❌ If user shares symptoms (fever, pain, dizziness, weakness, etc.):
→ Reply ONLY:
"For symptoms, please consult a qualified doctor. Tests should be done only after doctor’s advice."

❌ If user asks anything unrelated:
→ Reply ONLY:
"Sorry, I can only help with lab tests and related services."

❌ If user asks sensitive/unsafe topics (medical decisions, emergencies, personal health judgment):
→ Politely refuse and redirect to doctor.

⚠️ Never explain too much.
⚠️ Never guess.
⚠️ Never go outside scope.

💬 Tone:
- Friendly
- Clear
- Short
- Human-like (not robotic)
"""
lab_tests=[
    
    {
      "name": "ABSOLUTE EOSINOPHILS COUNT (AEC)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ALBUMIN SERUM",
      "price": 70,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ALKALINE PHOSPHATASE (ALP)",
      "price": 120,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "AMYLASE, SERUM",
      "price": 300,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BILIRUBIN TOTAL",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BILIRUBIN DIRECT",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BILIRUBIN INDIRECT",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BLEEDING TIME (BT)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BIOOD GROUPING (ABO) &RHFACTOR",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BIOOD UREA NITROGEN (BUN)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CALCIUM, SERUM",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CALCIUM, IONZED",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "C. HDL",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CHOLESTEROL TOTAL",
      "price": 120,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "CLOITING TIME (CT)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "COMPLETE BIOOD COUNT (CBC)",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "C-REACTIVE PROTEIN (CRP)",
      "price": 350,
      "pre_test_guideline": "No special preparation required"
    },
    
    {
      "name": "ABSOLUTE EOSINOPHILS COUNT (AEC)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ALBUMIN SERUM",
      "price": 70,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ALKALINE PHOSPHATASE (ALP)",
      "price": 120,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "AMYLASE, SERUM",
      "price": 300,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BILIRUBIN TOTAL",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BILIRUBIN DIRECT",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BILIRUBIN INDIRECT",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BLEEDING TIME (BT)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BIOOD GROUPING (ABO) &RHFACTOR",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BIOOD UREA NITROGEN (BUN)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CALCIUM, SERUM",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CALCIUM, IONZED",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "C. HDL",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CHOLESTEROL TOTAL",
      "price": 120,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "CLOITING TIME (CT)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "COMPLETE BIOOD COUNT (CBC)",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "C-REACTIVE PROTEIN (CRP)",
      "price": 350,
      "pre_test_guideline": "No special preparation required"
    },
      
    {
      "name": "PACKED CELL VOLUME (PCV / HAEMATOCRIT)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "PLATELET COUNT",
      "price": 120,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "POTASSIUM (K)",
      "price": 280,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "RA FACTOR (QUANTITATIVE)",
      "price": 350,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "SEMEN ANALYSIS",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "SGOT (AST)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "SGPT (ALT)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "SODIUM (Na)",
      "price": 280,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "SPUTUM FOR AFB",
      "price": 300,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "STOOL R/E (ROUTINE EXAMINATION)",
      "price": 200,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "STOOL EXAMINATION, OCCULT BLOOD",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "SUGAR BLOOD / SERUM FASTING / POST PRANDIAL / RANDOM",
      "price": 50,
      "pre_test_guideline": "No special preparation required",
      "note": "Price is ₹50 each"
    },
    {
      "name": "SUGAR BLOOD / BY GLUCOMETER",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "TOTAL LEUCOCYTE COUNT (TLC)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "TOTAL PROTEIN",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "TRIGLYCERIDES, SERUM",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "TYPHIDOT",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "UREA, BLOOD / SERUM",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "URIC ACID, SERUM",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "URINE FOR BILE SALT & BILE PIGMENT",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "URINE EXAMINATION, COMPLETE",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
      
    {
      "name": "URINE FOR PREGNANCY TEST (UPT)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "URINE R/E & M/E (ROUTINE & MICROSCOPIC EXAMINATION)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "URINE FOR SUGAR",
      "price": 40,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "VDRL",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "WIDAL SLIDE AGGLUTINATION TEST",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "WIDAL TUBE AGGLUTINATION TEST",
      "price": 500,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "THYROID PROFILE TOTAL",
      "price": 350,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "BETA HCG TOTAL (MATERNAL)",
      "price": 700,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "PROTHROMBIN TIME STUDIES",
      "price": 350,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "CULTURE URINE",
      "price": 850,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "VITAMIN D 25 HYDROXY",
      "price": 1530,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "VITAMIN B12 (CYANOCOBALAMIN)",
      "price": 1180,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "IRON STUDIES",
      "price": 550,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "TESTOSTERONE, TOTAL",
      "price": 700,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HEPATITIS C VIRAL RNA (HCV RNA) QUANTITATIVE ULTRA",
      "price": 1800,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HEPATITIS B SURFACE ANTIGEN (HBsAg), QUANTITATIVE",
      "price": 1800,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BAYA PANEL - 1",
      "price": 1100,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "BAYA PANEL - 2",
      "price": 1400,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "IMMUNOGLOBULIN IgE",
      "price": 900,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "SU - SW - 1",
      "price": 1050,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },

    {
      "name": "SU - SW - 2",
      "price": 1350,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "SU - SW - 3",
      "price": 1750,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "SU - SW - 4",
      "price": 2350,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "COMPLETE ALLERGY PANEL",
      "price": 5500,
      "pre_test_guideline": "No special preparation required"
    }
]

def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    return ' '.join(text.split())


def get_abbreviations(name):
    matches = re.findall(r'\((.*?)\)', name)

    abbrs = []

    for match in matches:
        for part in match.split('/'):
            abbrs.append(normalize(part))

    return abbrs


def search_lab_test(user_input):

    query = normalize(user_input)

    best_match = None
    best_overlap = 0

    for test in lab_tests:

        test_name = normalize(test["name"])

        # 1. Exact match
        if query == test_name:
            return test

        # 2. Contains match
        if query and query in test_name:
            return test

        # 3. Abbreviation match
        abbrs = get_abbreviations(test["name"])

        if query in abbrs:
            return test

        # 4. Token overlap scoring

        query_words = set(query.split())

        test_words = set(test_name.split())

        overlap = len(
            query_words.intersection(test_words)
        )

        if overlap > best_overlap:
            best_overlap = overlap
            best_match = test

    # At least 1 meaningful word should match
    if best_overlap > 0:
        return best_match

    return None

    # Only search if user is asking about tests/prices

    keywords = [
        "price",
        "rate",
        "cost",
        "test",
        "fasting",
        "preparation",
        "charge",
        "rupee",
        "₹"
    ]

    is_test_question = any(
        word in query for word in keywords
    )


    if not is_test_question:
        return None



    aliases = {
    "cbc": "COMPLETE BLOOD COUNT (CBC)",
    "vit d": "VITAMIN D 25 HYDROXY",
    "vitamin d": "VITAMIN D 25 HYDROXY",
    "b12": "VITAMIN B12 (CYANOCOBALAMIN)",
    "vitamin b12": "VITAMIN B12 (CYANOCOBALAMIN)",
    "lft": "LIVER FUNCTION TEST (LFT)",
    "liver": "LIVER FUNCTION TEST (LFT)",
    "kft": "KIDNEY FUNCTION TEST (KFT/RFT)",
    "kidney": "KIDNEY FUNCTION TEST (KFT/RFT)",
    "hba1c": "GLYCOSYLATED HEMOGLOBIN (HbA1C)",
    "lipid": "LIPID PROFILE",

    # ADD THESE
    "urea": "BLOOD UREA NITROGEN (BUN)",
    "bun": "BLOOD UREA NITROGEN (BUN)",
    "creatinine": "CREATININE, SERUM",
    "sugar": "GLUCOSE TOLERANCE TEST (GTT) 4 BLOOD & URINE SAMPLE"
    }


    for key, value in aliases.items():

        if key in query:

            for test in lab_tests:

                if value.lower() == test["name"].lower():
                    return test



    for test in lab_tests:

      name = test["name"].lower()

      words = name.split()

    # partial word matching

      for word in words:

        if len(word) > 3 and word in query:
            return test


    return None


# =========================
# MAIN CHAT FUNCTION
# =========================

def get_ai_response(user_input: str):

    print("User:", user_input)


    # FIRST: Check BAYA PATH LAB DATABASE

    lab_result = search_lab_test(user_input)


    if lab_result:

        reply = f"""
BAYA PATH LAB Investigation Details

Test:
{lab_result['name']}

Rate:
₹{lab_result['price']}

Pre-test Guideline:
{lab_result['pre_test_guideline']}
"""

        return reply.strip()



    # SECOND: Use AI model

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input)
    ]


    response = chat_model.invoke(messages)

    if "price" in user_input.lower() or "cost" in user_input.lower():
      return "Sorry, please contact BayaPathLab for exact test price details."

    print("AI:", response.content)

    return response.content