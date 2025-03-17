from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from fuzzywuzzy import process
import sqlite3

app = Flask(__name__)
CORS(app)  # Allow all domains to access the API

# Function to create the database and table if not exists
def init_db():
    conn = sqlite3.connect('swiggy_chatbot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')

    # Insert default questions (if empty)
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        default_questions = [
            ("What is the menu for today?", "Our menu for today includes a variety of delicious dishes."),
            ("What is the price of the dish?", "The price of the dish is Rs. 100."),
            ("How can I place an order?", "You can place an order by calling us at 1234567890."),
            ("What are your delivery timings?", "We deliver from 10 AM to 10 PM."),
            ("Do you have vegetarian options?", "Yes, we offer a variety of vegetarian dishes."),
            ("Can I customize my order?", "Yes, you can customize your order by selecting preferences."),
            ("Do you offer home delivery?", "Yes, we offer home delivery within a 5km radius."),
            ("What payment methods do you accept?", "We accept cash, credit/debit cards, and online payments."),
            ("Is there a minimum order value?", "Yes, the minimum order value is Rs. 200."),
            ("Can I cancel my order?", "Yes, orders can be canceled within 5 minutes of placing them."),
        ]
        cursor.executemany("INSERT INTO questions (question, answer) VALUES (?, ?)", default_questions)
        conn.commit()

    conn.close()


# Initialize the database
init_db()

# Function to get an answer from the database
def get_answer(question):
    conn = sqlite3.connect('swiggy_chatbot.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT answer FROM questions WHERE question = ?", (question,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else "Sorry, I don't know the answer."

# Function to find the closest matching question
def find_closest_match(user_question):
    conn = sqlite3.connect('swiggy_chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM questions")
    questions = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Find the best match with a similarity score
    closest_match, score = process.extractOne(user_question, questions)

    # Return the match only if it's at least 70% similar
    return closest_match if score > 70 else None

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_question = data.get("message", "").strip()

        # First, try to find the exact question
        bot_response = get_answer(user_question)
        if bot_response:
            return jsonify({"response": bot_response})

        # If no exact match, find the closest similar question
        closest_match = find_closest_match(user_question)
        if closest_match:
            return jsonify({"response": f"Did you mean: '{closest_match}'?"})

        # If no close match is found
        return jsonify({"response": "Sorry, I don't understand your question."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
