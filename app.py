from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session

def process_commit_log(text):
    # Regular expression to match ENG entries with their authors
    pattern = r'(ENG-\d+)\((feat|fix|chore|hotfix)\):\s*([^@\n]+?)(?:\s+@([a-zA-Z0-9-]+)|\s*$)'
    
    # Print the input text for debugging
    print("\nInput text lines:")
    for line in text.split('\n'):
        if 'ENG-' in line:
            print(f"Found ENG line: {line}")
    
    # Find all matches
    matches = re.finditer(pattern, text, re.MULTILINE)
    
    # Create a list of dictionaries with the extracted information
    entries = []
    for match in matches:
        description = match.group(3).strip()
        # Clean up the description
        description = re.sub(r'\s*\(.*$', '', description)  # Remove everything after and including (
        description = description.strip()
        
        entry = {
            'eng_number': match.group(1),
            'type': match.group(2),
            'description': description,
            'author': match.group(4) if match.group(4) else ''
        }
        entries.append(entry)
        print(f"Successfully matched entry: {entry}")  # Debug print
    
    # Sort entries by type (feat, fix, chore, hotfix)
    type_order = {'feat': 0, 'fix': 1, 'chore': 2, 'hotfix': 3}
    sorted_entries = sorted(entries, key=lambda x: type_order[x['type']])
    
    print(f"\nTotal entries found: {len(entries)}")  # Debug print
    return sorted_entries

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '')
        print("Received input:", user_input)  # Debug print
        # Process the input using our commit log processor
        output = process_commit_log(user_input)
        # Store the output in session
        session['output'] = output
        return redirect(url_for('results'))
    return render_template('index.html')

@app.route('/results')
def results():
    output = session.get('output')
    if output is None:
        return redirect(url_for('index'))
    return render_template('results.html', output=output)

if __name__ == '__main__':
    app.run(debug=True, port=8080) 