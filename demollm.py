import re
from dotenv import load_dotenv

from langchain_huggingface import (
ChatHuggingFace,
HuggingFaceEndpoint
)

from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# -------------------------

# MODEL

# -------------------------

llm = HuggingFaceEndpoint(
repo_id="meta-llama/Llama-3.1-8B-Instruct",
task="text-generation",
temperature=0.1,
max_new_tokens=150
)

model = ChatHuggingFace(llm=llm)

# -------------------------

# LAB TEST DATA

# -------------------------

# Put your full lab_tests list here

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
      "name": "CREATININE, SERUM",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "DENGUE FEVER COMB.PANET NS1 Ag ANTIBODY LgG &LgM",
      "price": 800,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "(DLC)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ELECTROLYTES (Na, K, Ca) SERUM",
      "price": 300,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ERYHROEYTE SEDIMENTATION RATE (ESR) WINTROD's",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "GLUCOSE TOLERANEE TAST (GTT) 4 BIOOD & URINE SAMPLE",
      "price": 320,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "GIYCOSYLATED HEMOGINDIN (HBAIC)",
      "price": 500,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HEMOGLOBIN(HB%)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HB%. TLC. DLC, ESR",
      "price": 180,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HEMOGRAM (CBC&ESR)",
      "price": 300,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HBsAg",
      "price": 200,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HCV",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HIV1/2",
      "price": 200,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "KIDNEY FUNCTION TEST (KFT/RFT) (UREA, CREATININE, URIC)",
      "price": 650,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "LIPASE, SERUM",
      "price": 620,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "LIPID PROFILE",
      "price": 400,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "LIVER FUNCTION TEST (LFT) (BILIRUBIN-TOTAL, DIREET, SGOT, SGPT, ALKALINE PHOSPHATASE)",
      "price": 450,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "SGOT, SGPT, ALKALINE PHOSPHATASE)",
      "price": 280,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "MANATOUX TEST/ PPD",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "MP BY CARD (ANTIGEN CARD)",
      "price": 150,
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


# -------------------------

# CONTEXT BUILDER

# -------------------------

def build_context():


  rows = []

  for test in lab_tests:
      rows.append(
          f"""
  ```

  Test: {test['name']}
  Price: ₹{test['price']}
  Preparation: {test['pre_test_guideline']}
  """
  )

  
  return "\n".join(rows)


CATALOG_CONTEXT = build_context()

# -------------------------

# PROMPT

# -------------------------

prompt = ChatPromptTemplate.from_messages([
(
"system",
"""

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


Rules:

* Answer only using provided context.
* Match abbreviations and partial names.
* Find the closest matching test.
* Never guess.
* If test not found, say:
  "This test is not available in our catalog."

Keep answers short and simple Hinglish.
"""
),
(
"human",
"""
Context:

{context}

Question:

{question}
"""
)
])

# -------------------------

# PRICE RANGE HANDLER

# -------------------------

def get_tests_under_price(limit):


  results = [
      t for t in lab_tests
      if t["price"] <= limit
  ]

  if not results:
      return f"₹{limit} ke andar koi test available nahi mila."

  lines = [
      f"{t['name']} - ₹{t['price']}"
      for t in results
  ]

  return (
      f"₹{limit} ke andar available tests:\n\n"
      + "\n".join(lines)
  )
  

  # -------------------------

  # MAIN CHAT

  # -------------------------
def get_ai_response(question: str):


    q = question.lower()

    # under 500
    m = re.search(
        r"(under|below|less than)\s*(₹)?\s*(\d+)",
        q
    )

    if m:
        limit = int(m.group(3))
        return get_tests_under_price(limit)

    # 500 ke andar
    m = re.search(
        r"(\d+)\s*(ke andar|se kam)",
        q
    )

    if m:
        limit = int(m.group(1))
        return get_tests_under_price(limit)

    messages = prompt.format_messages(
        context=CATALOG_CONTEXT,
        question=question
    )

    response = model.invoke(messages)

    return response.content

