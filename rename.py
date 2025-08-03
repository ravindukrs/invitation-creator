import fitz  # PyMuPDF
import re
import os
import glob
from shutil import copyfile

input_folder = "university"
output_folder = "university_invitees"
os.makedirs(output_folder, exist_ok=True)

def extract_invitee_name(pdf_path):
    doc = fitz.open(pdf_path)
    
    # For 2-page PDFs, focus on the second page which likely contains the invitee info
    if len(doc) >= 2:
        page = doc[1]  # Second page (0-indexed)
        blocks = page.get_text("blocks")
        
        # Sort blocks by position - we'll look for names anywhere on the page
        sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # Sort by y then x
        
        for i, block in enumerate(sorted_blocks):
            text = block[4].strip()
            if text and len(text) > 2:  # Only show meaningful text
                
                # Look for the spaced-out name pattern like "M R .  C H A M A R A  S H A L I N DA"
                spaced_name_pattern = r'^M\s*R\s*\.?\s*[A-Z\s]+$|^M\s*R\s*S\s*\.?\s*[A-Z\s]+$|^M\s*I\s*S\s*S\s*\.?\s*[A-Z\s]+$|^M\s*S\s*\.?\s*[A-Z\s]+$'
                
                if re.match(spaced_name_pattern, text, re.IGNORECASE):
                    # Keep the original spaced text to understand word boundaries
                    original_text = text.strip().upper()
                    
                    # Remove dots first
                    clean_text = re.sub(r'\.', '', original_text)
                    
                    # Split by multiple spaces to identify word boundaries
                    # The pattern "M R .  C H A M A R A  S H A L I N DA" has:
                    # - Single spaces between letters of the same word
                    # - Multiple spaces between different words
                    
                    # First, let's identify the title
                    title_match = re.match(r'^(M\s*R\s*S|M\s*I\s*S\s*S|M\s*R|M\s*S)\s*', clean_text)
                    if title_match:
                        title_part = title_match.group(1)
                        title = re.sub(r'\s+', '', title_part)  # Remove spaces from title
                        rest = clean_text[title_match.end():]
                    else:
                        title = ''
                        rest = clean_text
                    
                    # Now split the rest by looking for larger gaps (multiple spaces)
                    # Replace multiple spaces with a delimiter, then split
                    words_with_spaces = re.sub(r'\s{2,}', '|', rest)  # Replace 2+ spaces with |
                    word_groups = words_with_spaces.split('|')
                    
                    # Clean up each word group by removing single spaces
                    words = []
                    for group in word_groups:
                        if group.strip():
                            clean_word = re.sub(r'\s+', '', group.strip())
                            if len(clean_word) >= 2:  # Only keep meaningful words
                                words.append(clean_word)
                    
                    # Combine title and words
                    if title and words:
                        final_name = title + '_' + '_'.join(words)
                    elif title:
                        final_name = title
                    elif words:
                        final_name = '_'.join(words)
                    else:
                        # Fallback to simple split if pattern detection fails
                        clean_name = re.sub(r'\s+', '', clean_text)
                        final_name = clean_name
                    
                    print(f"Found invitee: {final_name}")
                    doc.close()
                    return final_name
    
    doc.close()
    return None

def process_pdf(pdf_path):
    name = extract_invitee_name(pdf_path)
    base = os.path.basename(pdf_path)
    if name:
        new_filename = f"{name}.pdf"
    else:
        new_filename = f"UNKNOWN_{base}"

    dest_path = os.path.join(output_folder, new_filename)
    copyfile(pdf_path, dest_path)
    print(f"Copied to: {dest_path}")

# Process all PDFs in folder
pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))
for pdf in pdf_files:
    process_pdf(pdf)
