import os
import json
import fitz  # PyMuPDF
from datetime import datetime

# Input/output directories inside Docker container
INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def score_section(text, job_keywords):
    score = 0
    for word in job_keywords:
        if word in text.lower():
            score += 1
    return score

# Load persona
persona_path = os.path.join(INPUT_DIR, "persona.json")
if not os.path.isfile(persona_path):
    raise FileNotFoundError("❌ persona.json not found in /app/input")

with open(persona_path, "r", encoding="utf-8") as f:
    pdata = json.load(f)
    persona = pdata.get("persona", "").strip()
    job = pdata.get("job_to_be_done", "").strip()

if not persona or not job:
    raise ValueError("❌ Invalid or empty persona.json content")

job_keywords = job.lower().split()

# Find all PDFs in input folder
pdf_paths = [
    os.path.join(INPUT_DIR, f)
    for f in os.listdir(INPUT_DIR)
    if f.endswith(".pdf")
]

if not pdf_paths:
    raise FileNotFoundError("❌ No PDF files found in /app/input")

# Output structure
final_result = {
    "metadata": {
        "input_documents": [os.path.basename(f) for f in pdf_paths],
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.now().isoformat()
    },
    "extracted_sections": [],
    "subsection_analysis": []
}

# Process each PDF
for path in pdf_paths:
    fname = os.path.basename(path)
    try:
        doc = fitz.open(path)
    except Exception as e:
        print(f"⚠️ Error opening {fname}: {e}")
        continue

    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict").get("blocks", [])
        for b in blocks:
            for line in b.get("lines", []):
                text = " ".join([s["text"] for s in line.get("spans", [])]).strip()
                if len(text) < 10:
                    continue
                rank = score_section(text, job_keywords)
                if rank >= 3:
                    final_result["extracted_sections"].append({
                        "document": fname,
                        "page": page_num,
                        "section_title": text,
                        "importance_rank": rank
                    })
                    final_result["subsection_analysis"].append({
                        "document": fname,
                        "page": page_num,
                        "refined_text": text
                    })

# Save output
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, "1B_output.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=2, ensure_ascii=False)

print(f"✅ Output saved to: {output_path}")
