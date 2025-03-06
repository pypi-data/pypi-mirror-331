import re
import os
import argparse

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod


def md_to_latex(md_text):
    # Convert Headers
    md_text = re.sub(r'^# (.*)', r'\\section{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'\s+}', '}', md_text)
    md_text = re.sub(r'^## (.*)', r'\\subsection{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^### (.*)', r'\\subsubsection{\1}', md_text, flags=re.MULTILINE)

    
    # Convert figured to Latex
    def convert_figure(match):
        image_path = match.group(1).strip()
        caption = match.group(2).strip() if match.group(2) else ""
        return (f"\\begin{{figure}}[h]\n\\centering\n"
                f"\\includegraphics[width=0.8\\textwidth]{{{image_path}}}\n"
                f"\\caption{{{caption}}}\n\\end{{figure}}") if caption else (
                f"\\begin{{figure}}[h]\n\\centering\n"
                f"\\includegraphics[width=0.8\\textwidth]{{{image_path}}}\n\\end{{figure}}")
    
    pattern = r'!\[\]\((.*?)\)\s*((?:Figura|Figure|Fig.)\s+\d+(?:\.\d+)?\s*.*?)\n'
    md_text = re.sub(pattern, convert_figure, md_text, flags=re.DOTALL)

    # !\[\]\((.*?)\)	Matches an image reference ![](path/to/image.jpg), capturing the path.
    # \s* → Matches any whitespace (spaces, newlines, etc.).
    # Figure \d+	 Matches "Figure" followed by a number.
    #  [^.]* → Matches any characters except a period (.)
    # \. → Matches the period at the end of the caption
    
    
    # Convert Block Formulas with Captions to Latex
    def convert_equation(match):
        equation = match.group(1).strip()
        return f"\\begin{{equation}}\n{equation}\n\\end{{equation}}"

    md_text = re.sub(r'\$\$(.*?)\$\$', convert_equation, md_text, flags=re.DOTALL)
    
    # Convert Inline Formulas to Latex
    md_text = re.sub(r'\$(.*?)\$', r'\\(\1\\)', md_text)  # Inline math: $x^2$ -> \(x^2\)
    
    # Convert tables to Latex
    def convert_table(match):
        table_html = match.group(2)  # Captured table HTML
        caption_before = re.search(r'^\s*(Table [IVXLCDM\d]+.*?)$', match.group(1), re.MULTILINE) if match.group(1) else None
        caption_after = re.search(r'^\s*(Table [IVXLCDM\d]+.*?)$', match.group(3), re.MULTILINE) if match.group(3) else None
        # Use caption if available, otherwise default
        caption = caption_before.group(1) if caption_before else (caption_after.group(1) if caption_after else "Table caption")
        # Extract table rows
        rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)

        if not rows:
            return ""  # If no rows are found, return empty string (invalid table)

        # Detect number of columns
        first_row = re.findall(r'<t[dh]>(.*?)</t[dh]>', rows[0])
        num_columns = len(first_row) if first_row else 1  # Default to 1 if no columns detected

        # Start LaTeX table
        latex_table = "\\begin{table}[h]\n\\centering\n"
        latex_table += "\\begin{tabular}{" + "|c" * num_columns + "|}\n\\hline\n"
        for row in rows:
            cells = re.findall(r'<t[dh]>(.*?)</t[dh]>', row)
            latex_table += " & ".join(cells) + " \\\\\n\\hline\n"

        latex_table += f"\\end{{tabular}}\n\\caption{{{caption}}}\n\\end{{table}}\n"
        return latex_table


    table_pattern = re.compile(
        r'\s*((?:Table|Tabla)\s+[IVXLCDM\d]+[^.\n]*[:.]?)?'  # Accepts "Table II:", "Tabla 2." etc.
        r'\s*\n*'  # Allow one or more newlines between caption and tables
        r'\s*<html><body><table>(.*?)</table></body></html>'  # HTML table content
        r'\s*((?:Table|Tabla)\s+[IVXLCDM\d]+[^.\n]*[:.]?)?',  # Optional caption after
        re.DOTALL | re.IGNORECASE
    )
    md_text = re.sub(table_pattern, convert_table, md_text)
    
    
    #remove citations
    md_text = re.sub(r'\[\d+\][,\-]?', '', md_text)
    
    # remove anything after bibliography section
    pattern = r'(\\section\s*\{(REFERENCES|REFERENCIAS|BIBLIOGRAPHY|BIBLIOGRAFIA)\s*\}).*'
    md_text = re.sub(pattern, r'\1', md_text, flags=re.IGNORECASE | re.DOTALL)
    
    #add latex doc format
    md_text = "\\begin{document}\n\n" + md_text + "\n\\end{document}"
    
    return md_text 


def to_latex(input_file):
    
    pdf_file_name = os.path.basename(input_file)  
    name_without_suff = pdf_file_name.split(".")[0]

    local_image_dir = os.path.join(os.getcwd(), f"output_{name_without_suff}/images/")
    local_md_dir = os.path.join(os.getcwd(), f"output_{name_without_suff}/")
    
    image_dir = str(os.path.basename(local_image_dir))

    os.makedirs(local_image_dir, exist_ok=True)

    print(f"local_image_dir  {local_image_dir} local_md_dir as {local_md_dir}")

    image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)
    # read bytes
    reader1 = FileBasedDataReader("")
    pdf_bytes = reader1.read(input_file)  # read the pdf content
    
    # proc
    ## Create Dataset Instance
    ds = PymuDocDataset(pdf_bytes)
    
    ## inference
    if ds.classify() == SupportedPdfParseMethod.OCR:
        infer_result = ds.apply(doc_analyze, ocr=True)
        pipe_result = infer_result.pipe_ocr_mode(image_writer)
    
    else:
        infer_result = ds.apply(doc_analyze, ocr=False)
        pipe_result = infer_result.pipe_txt_mode(image_writer)
    
    
    ### dump markdown
    pipe_result.dump_md(md_writer, f"{name_without_suff}.md", local_md_dir)
    
    ### dump content list
    pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", local_md_dir)
    
    ### dump middle json
    pipe_result.dump_middle_json(md_writer, f'{name_without_suff}_middle.json')

    #################################################################################
    ## PARSER TO LATEX
    ################################################################################

    md_file = os.path.join(local_md_dir, f"{name_without_suff}.md") 
    
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
  
        latex_content = md_to_latex(md_content)

        output_file = os.path.join(local_md_dir, "output_latex.tex") 
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        print(f"CONVERTION TO Latex FINISHED: LaTeX file saved as {output_file}")
        
    except Exception as e:
        print(f"ERROR for parsing to latex:::::  {e}")
        
def main():
    parser = argparse.ArgumentParser(description="Convert documents to LaTeX format.")
    parser.add_argument("input_file", type=str, help="Path to the input file")
    args = parser.parse_args()
    
    to_latex(args.input_file)  # Call the function with the argument

if __name__ == "__main__":
    main()