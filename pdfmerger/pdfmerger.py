import PyPDF2
import sys
import os

def get_pdf_files():
    pdf_files = [f for f in os.listdir() if f.endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return []
    
    print("Available PDF files:")
    for i, file in enumerate(pdf_files, 1):
        print(f"{i}. {file}")
    
    selected = input("Enter the numbers of the files you want to merge (comma-separated): ")
    selected_indices = [int(x.strip()) - 1 for x in selected.split(',')]
    return [pdf_files[i] for i in selected_indices if 0 <= i < len(pdf_files)]

def get_page_range(file_name):
    while True:
        range_input = input(f"Enter page range for {file_name} (e.g., '1-5' or '1,3,5-7' or 'all'): ").lower()
        if range_input == 'all':
            return None
        try:
            pages = set()
            for part in range_input.split(','):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages.update(range(start - 1, end))
                else:
                    pages.add(int(part) - 1)
            return sorted(pages)
        except ValueError:
            print("Invalid input. Please try again.")

def merge_pdfs(files):
    merger = PyPDF2.PdfMerger()
    for file in files:
        page_range = get_page_range(file)
        if page_range is None:
            merger.append(file)
        else:
            with open(file, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                merger.append(file, pages=page_range)
    
    output_name = input("Enter the name for the merged PDF (default: 'combined.pdf'): ")
    if not output_name:
        output_name = 'combined.pdf'
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'
    
    merger.write(output_name)
    merger.close()
    print(f"PDFs merged successfully into {output_name}")

if __name__ == "__main__":
    files_to_merge = get_pdf_files()
    if files_to_merge:
        merge_pdfs(files_to_merge)
    else:
        print("No files selected for merging.")
