from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/run-tests', methods=['POST'])
def run_tests():
    data = request.json
    apis = data.get('apis', [])
    responses = []

    for api in apis:
        method = api.get('method', 'GET').upper()
        url = api.get('url', '')
        params = {param['key']: param['value'] for param in api.get('params', [])}
        headers = {header['key']: header['value'] for header in api.get('headers', [])}
        body = api.get('body', '')

        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, verify=False)
            elif method == 'POST':
                response = requests.post(url, params=params, headers=headers, data=body, verify=False)
            elif method == 'PUT':
                response = requests.put(url, params=params, headers=headers, data=body, verify=False)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, data=body, verify=False)
            else:
                response = {'error': 'Unsupported method'}
                responses.append(response)
                continue


            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                body = response.json()
            elif 'application/xml' in content_type or 'text/xml' in content_type:
                body = response.text
            else:
                body = response.text  # Fallback for other text formats


            responses.append({
                'status_code': response.status_code,
                'body': body,
                'content_type': content_type
            })

        except Exception as e:
            responses.append({'status_code': 'error', 'body': {'error': str(e)}, 'content_type': ''})

    return jsonify({'responses': responses})

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(debug=True)