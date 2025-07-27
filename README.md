# Adobe_1B
# Context-Aware Content Extraction

Given a persona and a job-to-be-done in `persona.json`, and one or more input PDFs, this solution:
- Automatically extracts relevant sections from the PDFs
- Scores each section based on relevance to the job
- Outputs the result in a structured JSON format

---

## 📁 Project Structure

├── analyser.py # Main logic for content extraction
├── Dockerfile # For containerization (AMD64 compatible)
├── requirements.txt # Python dependencies
├── input/ # Input files (PDFs + persona.json)
│ ├── persona.json
│ └── doc1.pdf
├── output/ # Output directory for 1B_output.json
│ └── 1B_output.json
└── README.md # This file

---

## 🧠 How It Works

- **Keyword Extraction:** Job-to-be-done is broken into keywords.
- **Relevance Scoring:** Sections from the PDFs are scored by keyword presence.
- **Filtering:** Sections with a score ≥ 3 are retained.
- **Result:** Sections are saved in `1B_output.json` with page number, text, and rank.

---

## 🧪 Sample Input Format

**`input/persona.json`**
```json
{
  "persona": "AI Research Scientist",
  "job_to_be_done": "Survey state-of-the-art methods for LLM fine-tuning"
}
```

## Run locally with Docker
### 1. Build Docker Image
```bash
docker build --platform linux/amd64 -t adobe_1b_solution .
```
### 2.Run Container
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  adobe_1b_solution
```
