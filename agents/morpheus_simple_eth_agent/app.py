from flask import Flask, request, jsonify

from chains_and_agents.morpheus_chain import process_nlq

app = Flask(__name__)


@app.route('/process_nlq', methods=['POST'])
def handle_nlq():
    nlq = request.json['NLQ']  # Access the NLQ query from the request body

    # TODO, split out system vs user message

    result = process_nlq(nlq)

    return jsonify({'result': result})  # Return the result as a JSON response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)  # Start the Flask development server
