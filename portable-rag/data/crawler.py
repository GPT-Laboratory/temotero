#
# Requires:
#  - pip install pymupdf
#

import os
import fitz  # PyMuPD

PAGE_SEPARATOR="\n\n\n\n"

def collect_files_with_suffixes(directory, *suffixes):
    """
    Recursively collects all files with any of the specified suffixes (case-insensitive) from the given directory.
    
    Parameters:
    directory (str): The root directory to search.
    *suffixes (str): Variable number of file suffixes to filter files by (e.g., '.txt', '.py', '.jpg').
    
    Returns:
    list: A list of absolute paths to the files that match any of the suffixes.
    """
    file_list = []
    suffixes = tuple(suffix.lower() for suffix in suffixes)  # Convert all suffixes to lowercase
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(suffixes):  # Check if the file ends with any of the suffixes
                file_list.append(os.path.join(os.path.relpath(root), file))
    
    return file_list

def join_raw_text_pages(pages: list[str]):
    return PAGE_SEPARATOR.join(pages)

def save_text_to_file(text, directory, filename):
    """
    Saves the processed text to a .txt file.
    """
    try:
        output_path = f"{directory}/{filename}"
        print(f"Saving text to: {output_path}[.txt]")
        with open(f"{output_path}.txt", "w", encoding="utf-8") as txt_file:
            txt_file.write(text)
    except Exception as e:
        print(f"Error saving text file {output_path}: {e}")
        #failed_files.append(output_path)

def process_pdf_file_page_by_page(file_path):
  # Check if the file is a PDF
  if not file_path.lower().endswith('.pdf'):
      return None  # Skip non-PDF files

  try:
      # Open the PDF
      doc = fitz.open(file_path)
      raw_text_pages = []

      # Check each page for text
      for page_num in range(doc.page_count):
          page = doc.load_page(page_num)
          text = page.get_text("text")
          raw_text_pages.append(text)
      return raw_text_pages

  except Exception as e:
      print(f"Error processing file {file_path}: {e}")
    

import argparse
# Initialize parser
parser = argparse.ArgumentParser(description = "This is a simple tool to convert PDF files to text")
parser.add_argument("-s", "--searchpath", help = "Specifies the search path for PDF files", required=True)
parser.add_argument("-o", "--outputpath", help = "Specifies the output path for processed files", required=True)
args = parser.parse_args()
if not os.path.isdir(args.searchpath):
    parser.error(f"'{args.searchpath}' is not a valid directory.")
if not os.path.isdir(args.outputpath):
    parser.error(f"'{args.outputpath}' is not a valid directory.")

# Example usage:
if __name__ == "__main__":
    directory_to_search = args.searchpath
    file_suffixes = (".pdf", ".txt", ".py", ".jpg")  # Case-insensitive list of suffixes
    files = collect_files_with_suffixes(directory_to_search, *file_suffixes)
    
    # Process collected files
    for file in files:
        pages = process_pdf_file_page_by_page(file)
        filename_to_save = file.split("/")[-1]
        print(f"{file} page count {len(pages)}")
        save_text_to_file(join_raw_text_pages(pages), args.outputpath, filename_to_save)
