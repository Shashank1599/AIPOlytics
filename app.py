import os
import time
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Import your existing functions
from start import (
    scrape_ipo_dashboard,
    get_page_source_with_selenium,
    parse_and_aggregate_data,
    get_ipo_analysis_with_gemini
)

app = Flask(__name__)
CORS(app)

# Cache to store IPO data
ipo_cache = {
    'current_ipos': [],
    'upcoming_ipos': [],
    'last_updated': None,
    'analyses': {}
}

def get_cached_ipos():
    """Get IPOs from cache or fetch new ones if cache is old"""
    current_time = datetime.now()
    
    # Check if cache is empty or older than 1 hour
    if (not ipo_cache['last_updated'] or 
        (current_time - ipo_cache['last_updated']).seconds > 3600):
        
        print("Fetching fresh IPO data...")
        current_ipos, upcoming_ipos = scrape_ipo_dashboard()
        ipo_cache['current_ipos'] = current_ipos if current_ipos else []
        ipo_cache['upcoming_ipos'] = upcoming_ipos if upcoming_ipos else []
        ipo_cache['last_updated'] = current_time
        
    return ipo_cache['current_ipos'], ipo_cache['upcoming_ipos']

def parse_analysis_sections(analysis_text):
    """Parse the Gemini analysis into structured sections"""
    sections = {}
    
    # Split by numbered sections
    lines = analysis_text.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for section headers (1., 2., etc. or **Section Name:**)
        if (line.startswith('**') and line.endswith(':**')) or \
           (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.'))):
            
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line.replace('*', '').replace(':', '').strip()
            if current_section.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                current_section = current_section[2:].strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/ipos')
def get_ipos():
    """API endpoint to get list of current and upcoming IPOs"""
    try:
        current_ipos, upcoming_ipos = get_cached_ipos()
        return jsonify({
            'success': True,
            'current_ipos': current_ipos,
            'upcoming_ipos': upcoming_ipos,
            'current_count': len(current_ipos),
            'upcoming_count': len(upcoming_ipos),
            'total_count': len(current_ipos) + len(upcoming_ipos),
            'last_updated': ipo_cache['last_updated'].isoformat() if ipo_cache['last_updated'] else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ipo/<ipo_type>/<int:ipo_index>/analyze')
def analyze_ipo(ipo_type, ipo_index):
    """API endpoint to analyze a specific IPO"""
    try:
        current_ipos, upcoming_ipos = get_cached_ipos()
        
        # Determine which IPO list to use
        if ipo_type == 'current':
            ipos = current_ipos
            type_label = "CURRENT"
        elif ipo_type == 'upcoming':
            ipos = upcoming_ipos
            type_label = "UPCOMING"
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid IPO type. Must be "current" or "upcoming"'
            }), 400
        
        if ipo_index >= len(ipos):
            return jsonify({
                'success': False,
                'error': f'IPO index out of range for {ipo_type} IPOs'
            }), 400
        
        ipo = ipos[ipo_index]
        ipo_key = f"{ipo_type}_{ipo_index}_{ipo['name']}"
        
        # Check if analysis is already cached
        if ipo_key in ipo_cache['analyses']:
            return jsonify({
                'success': True,
                'data': ipo_cache['analyses'][ipo_key]
            })
        
        # Perform analysis
        print(f"Analyzing {type_label} IPO: {ipo['name']}")
        
        html_content = get_page_source_with_selenium(ipo['url'])
        if not html_content:
            return jsonify({
                'success': False,
                'error': 'Could not retrieve IPO details page'
            }), 500
        
        aggregated_data = parse_and_aggregate_data(html_content)
        if not aggregated_data:
            return jsonify({
                'success': False,
                'error': 'Could not parse IPO data from the page'
            }), 500
        
        analysis_text = get_ipo_analysis_with_gemini(aggregated_data)
        analysis_sections = parse_analysis_sections(analysis_text)
        
        # Cache the analysis
        analysis_data = {
            'ipo': ipo,
            'ipo_type': ipo_type,
            'type_label': type_label,
            'raw_analysis': analysis_text,
            'sections': analysis_sections,
            'analyzed_at': datetime.now().isoformat()
        }
        
        ipo_cache['analyses'][ipo_key] = analysis_data
        
        return jsonify({
            'success': True,
            'data': analysis_data
        })
        
    except Exception as e:
        print(f"Error analyzing IPO: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh')
def refresh_ipos():
    """Force refresh IPO data"""
    try:
        ipo_cache['current_ipos'] = []
        ipo_cache['upcoming_ipos'] = []
        ipo_cache['last_updated'] = None
        ipo_cache['analyses'] = {}
        
        current_ipos, upcoming_ipos = get_cached_ipos()
        
        return jsonify({
            'success': True,
            'message': 'IPO data refreshed successfully',
            'current_count': len(current_ipos),
            'upcoming_count': len(upcoming_ipos),
            'total_count': len(current_ipos) + len(upcoming_ipos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)