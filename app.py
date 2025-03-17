from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import process
import sqlite3

app = Flask(__name__)
CORS(app)

# Temporary storage for tracking last suggested question
session_data = {}

# Function to create the database and insert default questions
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

    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        print("Database is empty! Inserting default questions.")
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

# Function to get an exact answer (Case-Insensitive)
def get_answer(question):
    conn = sqlite3.connect('swiggy_chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM questions WHERE LOWER(question) = LOWER(?)", (question,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Function to find the closest matching question
def find_closest_match(user_question):
    conn = sqlite3.connect('swiggy_chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM questions")
    questions = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not questions:
        return None

    closest_match, score = process.extractOne(user_question, questions)
    return closest_match if score > 50 else None


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip().lower()

        user_id = "default_user"  # Static user tracking (can be improved with sessions)

        # Handling "yes" or "no" responses
        if user_message in ["yes", "no"]:
            if user_id in session_data and session_data[user_id]:
                if user_message == "yes":
                    correct_question = session_data[user_id]
                    answer = get_answer(correct_question)
                    session_data[user_id] = None  # Clear stored question after use
                    return jsonify({"response": answer})
                else:
                    session_data[user_id] = None  # Clear stored question
                    return jsonify({"response": "Okay! Could you please rephrase your question?"})

        # Greeting responses
        greetings = ["hi", "hello", "hey", "good morning", "good evening"]
        if user_message in greetings:
            return jsonify({
                "response": "Hello! 😊 How can I assist you today?\nHere are some options:\n"
                            "- 📌 What is the menu for today?\n"
                            "- 📌 How can I place an order?\n"
                            "- 📌 What are your delivery timings?"
            })

        # Check for an exact answer
        bot_response = get_answer(user_message)
        if bot_response:
            return jsonify({"response": bot_response})

        # If no exact match, find a similar question
        closest_match = find_closest_match(user_message)
        if closest_match:
            session_data[user_id] = closest_match  # Store suggested question
            return jsonify({"response": f"Did you mean: '{closest_match}'?"})

        return jsonify({"response": "Sorry, I don't understand your question. Can you rephrase it?"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
