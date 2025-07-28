import os
import json
import fitz
import re
from pathlib import Path
from collections import Counter

def merge_nearby_lines(lines, threshold=5):
    """
    Merges text lines that are vertically close to each other and have
    similar font properties. This is the key to fixing fragmented text.
    """
    if not lines:
        return []

    merged_lines = []
    current_line = lines[0]

    for next_line in lines[1:]:
        # Check if lines are on the same page and vertically close
        if (next_line['page_num'] == current_line['page_num'] and
            abs(next_line['bbox'][1] - current_line['bbox'][3]) < threshold and
            abs(next_line['font_size'] - current_line['font_size']) < 1):
            
            # Merge text and update bounding box
            current_line['text'] += " " + next_line['text']
            current_line['bbox'] = (
                min(current_line['bbox'][0], next_line['bbox'][0]),
                min(current_line['bbox'][1], next_line['bbox'][1]),
                max(current_line['bbox'][2], next_line['bbox'][2]),
                max(current_line['bbox'][3], next_line['bbox'][3])
            )
        else:
            merged_lines.append(current_line)
            current_line = next_line
            
    merged_lines.append(current_line)
    return merged_lines

def get_all_text_lines(doc):
    """Extracts all text from a document, preparing it for merging."""
    lines = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    
                    text = "".join(s['text'] for s in spans).strip()
                    if not text:
                        continue

                    font_sizes = Counter(s['size'] for s in spans)
                    dominant_size = font_sizes.most_common(1)[0][0]
                    
                    lines.append({
                        "text": text,
                        "font_size": dominant_size,
                        "page_num": page_num,
                        "bbox": line['bbox']
                    })
    return lines

def extract_document_structure(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"title": f"Error: {e}", "outline": []}

    # 1. Extract raw lines
    raw_lines = get_all_text_lines(doc)
    
    # 2. Merge fragmented lines into logical ones
    lines = merge_nearby_lines(raw_lines)

    if not lines:
        doc.close()
        return {"title": "", "outline": []}

    # --- Title Extraction ---
    # Heuristic: Largest font size on the first page
    first_page_lines = [line for line in lines if line['page_num'] == 0]
    if not first_page_lines:
        extracted_title = ""
        title_bboxes = []
    else:
        max_font_size = max(line['font_size'] for line in first_page_lines)
        title_lines = [line for line in first_page_lines if line['font_size'] == max_font_size]
        
        # Concatenate if multiple lines have the max font size
        extracted_title = " ".join(line['text'] for line in title_lines)
        title_bboxes = [line['bbox'] for line in title_lines]

    # --- Heading Classification ---
    font_sizes = [line['font_size'] for line in lines]
    baseline_size = Counter(font_sizes).most_common(1)[0][0] if font_sizes else 12
    
    candidates = []
    for line in lines:
        if line['bbox'] in title_bboxes:
            continue
            
        # Heading characteristics: larger than body, not too long, not a list item
        if (line['font_size'] > baseline_size and len(line['text'].split()) < 20):
             candidates.append(line)
             
    # Classify based on relative font size
    if not candidates:
        outline = []
    else:
        heading_font_sizes = sorted(list(set([c['font_size'] for c in candidates])), reverse=True)
        size_to_level = {size: f"H{i+1}" for i, size in enumerate(heading_font_sizes[:4])} # Look for H1-H4
        
        headings = []
        for c in candidates:
            if c['font_size'] in size_to_level:
                headings.append({
                    "level": size_to_level[c['font_size']],
                    "text": c['text'],
                    "page": c['page_num'] + 1,
                    "bbox": c['bbox']
                })
        
        headings.sort(key=lambda h: (h['page'], h['bbox'][1]))
        outline = [{"level": h['level'], "text": h['text'], "page": h['page']} for h in headings]

    doc.close()
    return {"title": extracted_title, "outline": outline}

def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processing {pdf_file.name}...")
        data = extract_document_structure(pdf_file)
        if data:
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  -> Successfully created {output_file.name}")

if __name__ == "__main__":
    print("Starting PDF processing...")
    process_pdfs()
    print("Completed PDF processing.")