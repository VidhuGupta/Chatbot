from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Function to connect to the database
def connect_db():
    conn = sqlite3.connect('swiggy_chatbot.db')
    cursor = conn.cursor()
    return conn, cursor

# Function to retrieve an answer from the database
def get_answer(question):
    conn, cursor = connect_db()
    cursor.execute("SELECT answer FROM questions WHERE question = ?", (question,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Sorry, I don't have an answer for that."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get("message", "").strip()
    if not user_question:
        return jsonify({"error": "Please provide a valid message."}), 400

    bot_response = get_answer(user_question)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)
