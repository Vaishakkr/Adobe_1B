import os
import json
import fitz
from datetime import datetime

def score_section(text, job_keywords):
    score = 0
    for word in job_keywords:
        if word in text.lower():
            score += 1
    return score

persona_path = input("📥 Enter path to persona.json file: ").strip()
if not os.path.isfile(persona_path) or not persona_path.endswith("persona.json"):
    raise FileNotFoundError("❌ Invalid persona.json file path.")

pdf_paths = input("📥 Enter paths to PDF files (comma-separated): ").strip().split(",")
pdf_paths = [p.strip() for p in pdf_paths if p.strip().endswith(".pdf") and os.path.isfile(p)]

if not pdf_paths:
    raise ValueError("❌ No valid PDF files found.")

with open(persona_path, "r", encoding="utf-8") as f:
    pdata = json.load(f)
    persona = pdata.get("persona", "").strip()
    job = pdata.get("job_to_be_done", "").strip()

if not persona or not job:
    raise ValueError("❌ Invalid persona.json content")

job_keywords = job.lower().split()

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

os.makedirs("output", exist_ok=True)
output_path = os.path.join("output", "1B_output.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=2, ensure_ascii=False)

print(f"✅ Output saved to: {output_path}")
