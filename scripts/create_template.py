import os
import re

# current directory absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))

static_html_file_path = os.path.join(current_dir, '../gpt_code_ui/webapp/static/index.html')
template_file_path = os.path.join(current_dir, '../gpt_code_ui/webapp/templates/index.html')
r_reg_src = re.compile(r'(src|href)="([^"]+)"', flags=re.IGNORECASE|re.MULTILINE|re.DOTALL)

# Read the static html file
with open(static_html_file_path, 'r') as file:
    static_html = file.read()
    # change source of the script to flask func call as it is in the template with regex
    static_html = re.sub(r_reg_src, '\\1="{{APPLICATION_ROOT}}{{ url_for(\'static\', filename=\'\\2\') }}"', static_html)
    # Write the static html to the template file
    # ensure the template directory exists
    os.makedirs(os.path.dirname(template_file_path), exist_ok=True)
    with open(template_file_path, 'w') as template_file:
        template_file.write(static_html)