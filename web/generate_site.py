import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import markdown

def load_evaluations(logs_dir):
    """Load all evaluation JSON files from the logs directory"""
    evaluations = []
    for file in os.listdir(logs_dir):
        if file.endswith('.json'):
            with open(os.path.join(logs_dir, file), 'r') as f:
                data = json.load(f)
                # Extract filename without extension for the HTML file
                html_file = f"{os.path.splitext(file)[0]}.html"
                evaluations.append({
                    'data': data,
                    'filename': file,
                    'html_file': html_file
                })
    return evaluations

def generate_site(logs_dir, output_dir):
    """Generate static HTML site from evaluation JSON files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'static', 'css'), exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('web/templates'))
    
    # Load all evaluations
    evaluations = load_evaluations(logs_dir)
    
    # Copy CSS file
    css_src = os.path.join('web/static/css/style.css')
    css_dest = os.path.join(output_dir, 'static/css/style.css')
    os.makedirs(os.path.dirname(css_dest), exist_ok=True)
    with open(css_src, 'r') as src, open(css_dest, 'w') as dest:
        dest.write(src.read())
    
    # Generate index page
    template = env.get_template('index.html')
    index_data = []
    for eval_data in evaluations:
        data = eval_data['data']
        company_name = data['metadata'].get('company_name')
        index_data.append({
            'company_name': company_name if company_name is not None else 'Unknown Company',
            'date': data['metadata'].get('evaluation_date'),
            'overall_score': data.get('Overall', {}).get('score', 0),
            'link': eval_data['html_file']
        })
    
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(template.render(evaluations=index_data))
    
    # Generate individual evaluation pages
    template = env.get_template('evaluation.html')
    for eval_data in evaluations:
        data = eval_data['data']
        
        # Separate metadata, overall score, and dimensions
        metadata = data['metadata']
        overall = data.get('Overall', {})
        
        # Get all dimensions except metadata and overall
        dimensions = {k: v for k, v in data.items() 
                     if k not in ['metadata', 'Overall']}
        
        # Convert rationale to HTML
        for dim in dimensions.values():
            if 'rationale' in dim:
                # Replace single \n with double for markdown paragraphs, then convert
                dim['rationale_html'] = markdown.markdown(dim['rationale'].replace('\n', '\n\n'))
            else:
                dim['rationale_html'] = ''
        
        with open(os.path.join(output_dir, eval_data['html_file']), 'w') as f:
            f.write(template.render(
                metadata=metadata,
                overall=overall,
                dimensions=dimensions
            ))

if __name__ == '__main__':
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Set up paths
    logs_dir = project_root / 'logs'
    output_dir = project_root / 'docs'  # GitHub Pages uses /docs by default
    
    # Generate the site
    generate_site(logs_dir, output_dir) 