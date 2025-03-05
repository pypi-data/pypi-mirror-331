import os
import markdown
from xhtml2pdf import pisa
import re

def fix_list_indentation(line: str, in_list: bool) -> tuple[str, bool]:
    """Fix inconsistent list indentation and return if we're in a list."""
    stripped = line.lstrip()
    if not stripped:
        return line, in_list
    
    # Check for list markers
    is_list_item = bool(re.match(r'^[-*+]\s|^\d+\.\s', stripped))
    
    if is_list_item:
        # Ensure consistent indentation for nested lists
        indent_level = len(line) - len(stripped)
        if indent_level > 0:
            # Normalize to 2 spaces per level
            proper_indent = ' ' * ((indent_level // 2) * 2)
            return proper_indent + stripped, True
        return stripped, True
    elif in_list and line.startswith(' '):
        # Continue list item text with proper indentation
        return '  ' + stripped, True
    return line, False

import re

def is_misplaced_code_block(block_lines):
    """
    Heuristic to decide if a code block is actually accidental text.
    Return True if the block likely contains headings/lists/images etc.
    that should be normal markdown text, not code.
    """
    # If we see markdown features like headings (start with '#'),
    # bullet lists (-, +, *), numeric lists (1.), or image/link syntax,
    # we can guess it's not actual code.
    # Adjust this as needed for your own heuristics.
    for line in block_lines:
        # Heading or bullet or numeric list
        if re.match(r'^\s*(#{1,6}\s|[*+\-]\s|\d+\.\s)', line):
            return True
        
        # Common image/link syntax could also be a giveaway
        if '![ ' in line or re.search(r'!\[.*\]\(.*\)', line):
            return True
    
    # If none of the above patterns matched, we assume it's legit code
    return False


def fix_misplaced_code_blocks(lines):
    """
    Scan lines for triple-backtick code blocks.
    If a block seems to contain 'accidental' headings/lists,
    remove triple backticks so it is processed as normal text.
    """
    result = []
    code_block_lines = []
    in_code_block = False
    code_block_marker = ""

    for line in lines:
        # Detect opening/closing of code fences
        if re.match(r'^\s*```', line.strip()):
            if not in_code_block:
                # Entering a code block
                in_code_block = True
                code_block_marker = line  # store the backtick line
                code_block_lines = []
            else:
                # Exiting a code block: decide if it’s accidental text
                if is_misplaced_code_block(code_block_lines):
                    # It's actually text, so drop the backticks
                    result.extend(code_block_lines)
                else:
                    # Keep it as a code block
                    result.append(code_block_marker)  # opening backticks
                    result.extend(code_block_lines)
                    result.append(line)  # closing backticks
                # Reset flags
                in_code_block = False
                code_block_marker = ""
                code_block_lines = []
        else:
            if in_code_block:
                # Collect lines inside the code block
                code_block_lines.append(line)
            else:
                # Normal line outside a code block
                result.append(line)

    # If file ended in a code block without closing
    if in_code_block:
        # Decide for the unclosed block
        if is_misplaced_code_block(code_block_lines):
            result.extend(code_block_lines)
        else:
            result.append(code_block_marker)
            result.extend(code_block_lines)
            result.append("```")

    return result


def fix_emphasis_markers(text: str) -> str:
    """Fix common emphasis marker issues (* and _)."""
    # Fix spaces between emphasis markers
    text = re.sub(r'\* \*(.*?)\* \*', r'**\1**', text)
    text = re.sub(r'_ _(.*?)_ _', r'__\1__', text)
    
    # Fix unmatched emphasis markers
    open_stars = text.count('**')
    open_underscores = text.count('__')
    
    if open_stars % 2:
        text = text.replace('**', '*', 1)  # Convert to single star for odd counts
    if open_underscores % 2:
        text = text.replace('__', '_', 1)  # Convert to single underscore for odd counts
    
    return text

def fix_table_formatting(line: str) -> str:
    """Fix common table formatting issues."""
    if '|' in line:
        # Ensure proper spacing around pipe symbols
        line = re.sub(r'\|(?!\s)', '| ', line)
        line = re.sub(r'(?<!\s)\|', ' |', line)
        
        # Fix separator lines
        if re.match(r'^[\s|:-]+$', line):
            parts = line.split('|')
            fixed_parts = []
            for part in parts:
                part = part.strip()
                if part:
                    if ':' in part:
                        # Handle alignment markers
                        if part.startswith(':') and part.endswith(':'):
                            fixed_parts.append(':---:')
                        elif part.startswith(':'):
                            fixed_parts.append(':---')
                        elif part.endswith(':'):
                            fixed_parts.append('---:')
                        else:
                            fixed_parts.append('---')
                    else:
                        fixed_parts.append('---')
            line = '| ' + ' | '.join(fixed_parts) + ' |'
    return line

def clean_markdown(markdown_text: str) -> str:
    """
    Clean Markdown text by fixing common formatting issues and typos.
    """
    # 1) First split into lines
    lines = markdown_text.splitlines()

    # 2) Fix misplaced code blocks (if any)
    lines = fix_misplaced_code_blocks(lines)

    # 3) Now that accidental code blocks are turned back into normal lines,
    #    proceed with your existing "in_code_block" logic, etc.
    cleaned_lines = []
    in_code_block = False
    code_block_count = 0
    in_list = False
    prev_blank = False
    
    for line in lines:
        # Detect code block again (but now only real code blocks remain)
        if line.strip().startswith("```"):
            code_block_count += 1
            in_code_block = (code_block_count % 2 == 1)
            # If entering a code block and no language is specified, set default
            if in_code_block and line.strip() == "```":
                line = "```text"
            cleaned_lines.append(line)
            continue

        if not in_code_block:
            # Existing logic: blank lines, heading fixes, blockquotes, etc.
            if not line.strip():
                if not prev_blank:
                    cleaned_lines.append('')
                prev_blank = True
                continue
            prev_blank = False

            # Convert tabs to spaces
            line = line.replace('\t', '    ')

            # Fix list indentation, headings, emphasis, tables, etc.
            line, in_list = fix_list_indentation(line, in_list)

            # Possibly fix headings if they look like # # ...
            stripped_line = line.lstrip()
            if stripped_line.startswith('#'):
                ...
                # (your heading logic from before)

            # Fix blockquotes
            if line.lstrip().startswith('>'):
                line = re.sub(r'^\s*>', '>', line)
                line = re.sub(r'^>', '> ', line)

            # Fix emphasis markers
            line = fix_emphasis_markers(line)

            # Fix table formatting
            line = fix_table_formatting(line)

            # Fix reference link syntax
            line = re.sub(
                r'\[([^\]]+)\]:\s*([^\s]+)(?:\s+"([^"]+)")?',
                lambda m: f'[{m.group(1)}]: {m.group(2)}'
                          + (f' "{m.group(3)}"' if m.group(3) else ''),
                line
            )

        cleaned_lines.append(line)

    # If we ended with an unclosed real code block, close it
    if in_code_block:
        cleaned_lines.append("```")

    # Ensure file ends with exactly one newline
    result = "\n".join(cleaned_lines)
    return result.rstrip() + "\n"


def make_link_callback(base_path):
    """
    Create a link_callback function that resolves relative URIs using the provided base_path.
    """
    def link_callback(uri, rel):
        # If URI is absolute (i.e., a web URL), return it unchanged.
        if uri.startswith("http://") or uri.startswith("https://"):
            return uri

        # Build the absolute path relative to the Markdown file's directory.
        abs_path = os.path.join(base_path, uri)
        if not os.path.isfile(abs_path):
            raise Exception(f"File not found: {abs_path}")
        return abs_path

    return link_callback

def convert_html_to_pdf(source_html, output_filename, link_callback_func):
    """
    Convert HTML content to a PDF file using xhtml2pdf.
    """
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(source_html, dest=result_file, link_callback=link_callback_func)
    return pisa_status.err

def clean_html_whitespace(html):
    """
    Clean up whitespace in HTML output from markdown conversion.
    Specifically targets spacing issues around headers and paragraphs.
    """
    # Remove empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    
    # Remove empty paragraphs after headers
    html = re.sub(r'(</h[1-6]>)\s*<p>\s*</p>', r'\1', html)
    
    # Fix spacing between list items
    html = re.sub(r'(</li>)\s*<li>', r'\1<li>', html)
    
    # Remove extra space between paragraphs
    html = re.sub(r'(</p>)\s*<p>', r'\1<p>', html)
    
    return html

def markdown_to_pdf(markdown_text, output_pdf, base_path):
    """
    Convert Markdown text to a PDF file using markdown and xhtml2pdf.
    """
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_text, extensions=['extra', 'codehilite'])
    
    # Clean up whitespace issues in the generated HTML
    html_content = clean_html_whitespace(html_content)
    
    # Wrap the HTML in a compact document with strict spacing control
    html_template = f"""
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          /* Base body styles */
          body {{ 
            font-family: sans-serif; 
            padding: 20px; 
            line-height: 1.2;
          }}
          
          /* Control image size */
          img {{ max-width: 100%; height: auto; }}
          
          /* Zero margins for paragraphs */
          p {{ margin: 0; padding: 0; }}
          
          /* Tight header spacing */
          h1, h2, h3, h4, h5, h6 {{ 
            margin-top: 10px;
            margin-bottom: 5px;
            padding: 0;
          }}
          
          /* First header should have no top margin */
          body > h1:first-child, body > h2:first-child {{ margin-top: 0; }}
          
          /* Lists should be compact */
          ul, ol {{ 
            margin-top: 0; 
            margin-bottom: 0; 
            padding-top: 0; 
            padding-bottom: 0; 
          }}
          
          /* List items should be tight */
          li {{ 
            margin: 0; 
            padding: 0;
          }}
          
          /* Zero spacing for code blocks */
          pre {{ 
            margin: 0; 
            padding: 5px;
          }}
          
          /* Horizontal rule */
          hr {{
            margin: 10px 0;
            border: 0;
            height: 1px;
            background-color: #ddd;
          }}
        </style>
      </head>
      <body>
        {html_content}
      </body>
    </html>
    """
    
    # Create the link_callback using the provided base_path
    link_callback_func = make_link_callback(base_path)
    
    # Convert the HTML to PDF
    error = convert_html_to_pdf(html_template, output_pdf, link_callback_func)
    if error:
        print("An error occurred during PDF generation.")
    else:
        print(f"PDF generated successfully: {output_pdf}")

if __name__ == '__main__':
    # Path to your Markdown file
    md_filepath = '/Users/pouria/Documents/Coding/VideoInstruct/output/20250304_004159/documentation_v3_enhanced.md'
    # Determine the base directory from the Markdown file's absolute path
    base_path = os.path.dirname(os.path.abspath(md_filepath))
    
    # Read the Markdown file
    with open(md_filepath, 'r', encoding='utf-8') as file:
        md_text = file.read()

    # Clean the Markdown text
    cleaned_md_text = clean_markdown(md_text)
    
    # Generate the PDF with images resolved relative to the Markdown file's directory
    markdown_to_pdf(cleaned_md_text, 'output.pdf', base_path)
