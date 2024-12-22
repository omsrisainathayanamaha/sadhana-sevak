import vectorization
import get_text_from_pdf
import process_text

pdf_paths = ["sampledata/geeta.pdf"]
print("Extracting text from PDFs...")
get_text_from_pdf.extract_text_from_pdfs(pdf_paths, start_page=185, end_page=256) # this pdf actually has text in it
print("Text extracted from PDFs.")
print("Processing text...")
process_text.process_document("extracted_text.txt", "processed_text.txt")
print("Text processed.")
print("Vectorizing commentary...")
vectorization.vectorize_commentary()
print("Commentary vectorized. Proceed to run server.py and frontend.")

