from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()

llm= HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation"
)

model = ChatHuggingFace(llm=llm)

templates=ChatPromptTemplate.from_messages([
                                           ("system", """
You are a professional and safe AI assistant for BayaPathLab.
BayaPathLab is a Diagnostic Laboratory

📍 Location:
BayaPathLab is located in Near Thana, Kelakhera, District U.S. Nagar, Uttarakhand, India.

👨‍⚕️ Owner:
Dr. Sukhdev Singh

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
"""),
("human","""
Context:
{context}

Question:
{question}

Answer the question based only on the provided context.
                                           """)
])

context = """{
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
      "name": "BLOOD GROUPING (ABO) & RH FACTOR",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "BLOOD UREA NITROGEN (BUN)",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CALCIUM, SERUM",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CALCIUM, IONIZED",
      "price": 250,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "C. HDL CHOLESTEROL TOTAL",
      "price": 150,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "CLOTTING TIME (CT)",
      "price": 50,
      "pre_test_guideline": "Overnight fasting is mandatory"
    },
    {
      "name": "COMPLETE BLOOD COUNT (CBC)",
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
      "name": "DENGUE FEVER COMB. PANEL NS1 Ag ANTIBODY IgG & IgM",
      "price": 800,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "DLC",
      "price": 100,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ELECTROLYTES (Na, K, Ca) SERUM",
      "price": 300,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "ERYTHROCYTE SEDIMENTATION RATE (ESR) WINTROBE",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "GLUCOSE TOLERANCE TEST (GTT) 4 BLOOD & URINE SAMPLE",
      "price": 320,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "GLYCOSYLATED HEMOGLOBIN (HbA1C)",
      "price": 500,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HAEMOGLOBIN (HB%)",
      "price": 50,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HB%, TLC, DLC, ESR",
      "price": 180,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "HEMOGRAM (CBC & ESR)",
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
      "name": "HIV 1/2",
      "price": 200,
      "pre_test_guideline": "No special preparation required"
    },
    {
      "name": "KIDNEY FUNCTION TEST (KFT/RFT)",
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
      "name": "LIVER FUNCTION TEST (LFT)",
      "price": 450,
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
"""
def get_ai_response(question: str):
    

    messege=templates.format_messages(
        context=context,
        question=question
    )
    print("\nAI:")
    response=model.invoke(messege)
    print(response.content)
    return response.content