from pdf2image import convert_from_path
import pytesseract

def get_text_from_pdf(pdf_path, start_page=None, end_page=None):
    # Specify the page range for conversion
    pages = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
    extracted_text = ""
    for page in pages:
        text = pytesseract.image_to_string(page)
        extracted_text += text + "\n"
    return extracted_text

def get_text_from_pdfs(pdf_paths, start_page=None, end_page=None):
    extracted_text = "".join(
        get_text_from_pdf(pdf_path, start_page, end_page)
        for pdf_path in pdf_paths
    )
    # Save the extracted text to a file
    with open('extracted_text.txt', 'w') as f:
        f.write(extracted_text)
    return 'extracted_text.txt'
from PyPDF2 import PdfReader

def extract_text_from_pdfs(pdf_paths, start_page, end_page):
    extracted_text = ""
    
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        # Ensure the page range is valid
        start = max(start_page - 1, 0)  # Convert to 0-based index
        end = min(end_page, total_pages)
        
        for page_num in range(start, end):
            print(f"Extracting text from page {page_num + 1}...")
            page = reader.pages[page_num]
            extracted_text += page.extract_text() + "\n"
            print("Text extracted successfully.")
    
    # Write the extracted text to a file
    with open('extracted_text.txt', 'w') as f:
        f.write(extracted_text)
    
    return 'extracted_text.txt'

