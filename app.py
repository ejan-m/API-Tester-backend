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
        headers = {header['key']: header['value'] for header in api.get('headers', [])}
        body = api.get('body', '')

        # payload_content_type = headers.get('Content-Type', '')
        # if 'application/xml' in payload_content_type:
        #     body = {
        #         "Destination": url,
        #         "Message": body,
        #         "Note": "Modified by Shawn"
        #     }

        #     url = 'http://localhost:1003/api/Values/IPC_talk'
        #     headers = {'Content-Type': 'application/json'}

        # print(url)
        # print(body)
        print(method)
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, verify=False)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body, verify=False)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=body, verify=False)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=body, verify=False)
            elif method == 'MIPC':
                body = {
                    "Destination": url,
                    "Message": body,
                    "Note": "Modified by Shawn"
                }

                url = 'http://localhost:1003/api/Values/IPC_talk'

                response = requests.post(url, headers=headers, json=body, verify=False)
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