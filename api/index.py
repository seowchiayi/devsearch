from flask import Flask, jsonify, request
from faqGenerator import main as faq_generator
from faqGenerator import rate_limit_exceeded

app = Flask(__name__)

from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

class GETHandler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write('Hello, world!\n'.encode('utf-8'))
        python_version = f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"
        self.wfile.write(f'Python version {python_version}'.encode('utf-8'))

# variable required by Vercel
handler = GETHandler

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return "Hello, World!"

# This route is used to generate the FAQ from the markdown files in the repository
@app.route('/api/generate-faq', methods=['POST', 'GET'])
def generate_faq_route():
    if request.method == 'POST':
        url = request.json.get('urls')
        if url:
            try:
                user_id = request.headers.get('User-Id')

                if rate_limit_exceeded(user_id):
                    return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429  # Return 429 status code for rate limit exceeded
            
                faq = faq_generator(url)
                if faq == -1:
                    return jsonify({'error': 'Invalid URL is entered.'}), 400
                
                return jsonify({'faq': faq})
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'URL not provided'}), 400
    else:
        return jsonify({'error': 'bruh'}), 405
    
if __name__ == '__main__':
    app.run(debug=True, port=5328)
