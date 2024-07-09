from flask import Flask, request, jsonify
from flask_cors import CORS
from multistep_prompting.agent_manager_v2 import AgentManager
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

agent_manager = AgentManager()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    app.logger.debug(f"Received data: {data}")
    
    query = data.get('query')
    dzial_name = data.get('dzial')

    if not query or not dzial_name:
        app.logger.error(f"Missing query or dzial. Query: {query}, Dzial: {dzial_name}")
        return jsonify({'error': 'Missing query or dzial'}), 400

    # Find the dzial_info in the prompts
    dzial_info = next((dzial for dzial in agent_manager.prompts.get('dzialy', []) 
                       if dzial['nazwa'] == dzial_name), None)
    
    if not dzial_info:
        app.logger.error(f"Invalid dzial: {dzial_name}")
        return jsonify({'error': 'Invalid dzial'}), 400

    try:
        response = agent_manager.process_query(query, dzial_info)
        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your message'}), 500

@app.route('/api/dzialy', methods=['GET'])
def get_dzialy():
    dzialy = [dzial['nazwa'] for dzial in agent_manager.prompts.get('dzialy', [])]
    app.logger.debug(f"Available dzialy: {dzialy}")
    return jsonify({'dzialy': dzialy})

if __name__ == '__main__':
    app.run(debug=True)