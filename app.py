from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pyodbc

app = Flask(__name__)
CORS(app)

# Define the connection parameters
server = 'TAMSSDBA02'  
database = 'Ops_WorkLoad_Analysis'
username = 'mtb_owa'
password = 'MTB_owa123456789'

# Create the connection string
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Table structure:
# CREATE TABLE [Ops_WorkLoad_Analysis].[dbo].[API_Info] (
#     Id INT PRIMARY KEY IDENTITY(1,1),
#     Scenario_Name NVARCHAR(255),
#     API_Name NVARCHAR(255),
#     Method NVARCHAR(10),
#     URL NVARCHAR(500),
#     Destination NVARCHAR(500),
#     Header NVARCHAR(MAX),
#     body NVARCHAR(MAX),
#     ChainParams NVARCHAR(MAX)
# )


@app.route('/save-scenario', methods=['POST'])
def save_scenario():
    data = request.json
    scenario_name = data.get('scenarioName', '')
    apis = data.get('apis', [])
    for api in apis:
        method = api.get('method', 'GET')
        url = api.get('url', '')
        destination = api.get('destination', '') if method == 'MIPC' else ''
        headers = api.get('headers', [])
        body = api.get('jsonBody', '') if method != 'MIPC' else api.get('xmlBody', '')
        chain_params = api.get('chainParams', [])
        # Convert headers and chain_params to JSON strings
        headers_str = str(headers)
        chain_params_str = str(chain_params)
        print(scenario_name, api['name'], method, url, destination, headers_str, body, chain_params_str)
        cursor.execute("""
            INSERT INTO [Ops_WorkLoad_Analysis].[dbo].[API_Info] (Scenario_Name, API_Name, Method, URL, Destination, Header, Body, ChainParams)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (scenario_name, api['name'], method, url, destination, headers_str, body, chain_params_str))
    conn.commit()
    return jsonify({'message': 'Scenario saved successfully'}), 201


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

        print(method)
        print(body)

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