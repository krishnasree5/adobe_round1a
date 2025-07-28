# PDF Outline Extractor - Adobe India Hackathon Round 1A

## Approach

This solution extracts structured document outlines (titles and headings) from PDFs as per the Adobe India Hackathon Round 1A specifications. The approach involves the following steps:

1. **Parsing Text and Metadata**:

   * Extracts all text blocks from the PDF using `PyMuPDF` (`fitz`).
   * Gathers positional and font size metadata for each line.

2. **Merging Fragmented Lines**:

   * Lines that are vertically close and share font properties are merged to fix broken sentences or headings.

3. **Title Detection**:

   * On the first page, the line(s) with the largest font size are identified and merged as the document title.

4. **Heading Detection and Classification**:

   * Lines with font size larger than the document's baseline are shortlisted.
   * These are ranked by font size and mapped to heading levels (H1-H4).
   * Lines are filtered to exclude long body text or list items.

5. **Final Output Structure**:

   * The extracted title and heading outlines are saved as JSON in the following format:

```json
{
  "title": "Document Title Here",
  "outline": [
    {"level": "H1", "text": "Section Heading", "page": 1},
    ...
  ]
}
```

## Libraries Used

* `PyMuPDF` (fitz): For reading PDF content, extracting text and metadata.
* `collections.Counter`: For font size aggregation.
* `pathlib`: For clean file system operations.
* `json`: For structured output.

## How to Build and Run

### 1. **Docker Build**

Ensure you're in the project root directory with the required files (`process_pdfs.py`, `input/`, `output/`, `Dockerfile`).

```bash
docker build --platform linux/amd64 -t adobe_round1a:krish2025 .
```

### 2. **Run the Container**

Use the following Docker command to execute the solution (matches the "Expected Execution"):

#### Git Bash (Linux-like):

```bash
docker run --rm \
  -v "/c/Users/YourName/Desktop/project/input:/app/input" \
  -v "/c/Users/YourName/Desktop/project/output:/app/output" \
  --network none \
  adobe_round1a:krish2025
```

#### PowerShell:

```powershell
docker run --rm `
  -v "${PWD}\input:/app/input" `
  -v "${PWD}\output:/app/output" `
  --network none `
  adobe_round1a:krish2025
```

### 3. **Expected Behavior**

* The container will:

  * Process all `.pdf` files from `/app/input`
  * Generate corresponding `.json` outputs in `/app/output`
  * Format output with title and structured headings (H1–H4)

### 4. **Directory Structure**

```
.
├── Dockerfile
├── process_pdfs.py
├── input/
│   ├── file01.pdf
│   └── file02.pdf
└── output/
    ├── file01.json
    └── file02.json
```
