import sqlite3

# Connect to the database
conn = sqlite3.connect('swiggy_chatbot.db')
cursor = conn.cursor()

# Create a table to store questions and answers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )
''')

# Create a function to store a question and answer in the database
def store_question_answer(question, answer):
    cursor.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()

# Create a function to retrieve an answer from the database based on a question
def get_answer(question):
    cursor.execute("SELECT answer FROM questions WHERE question = ?", (question,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Create a function to generate a response to a question
def generate_response(question):
    # This is a simple implementation that returns a default response
    # You can replace this with a more sophisticated NLP-based response generator
    default_responses = {
        "what is the menu for today?": "Our menu for today includes a variety of delicious dishes.",
        "what is the price of the dish?": "The price of the dish is Rs. 100.",
        "how can i place an order?": "You can place an order by calling us at 1234567890 or by visiting our website.",
        "what is your menu today?": "Our menu for today includes a variety of delicious dishes.",
        "menu for today": "Our menu for today includes a variety of delicious dishes.",
        "today's menu": "Our menu for today includes a variety of delicious dishes."
    }
    return default_responses.get(question.lower(), None)

# Create a function to find the closest matching question in the database
def find_closest_matching_question(question):
    cursor.execute("SELECT question FROM questions")
    results = cursor.fetchall()
    closest_match = None
    max_match_count = 0
    for result in results:
        match_count = sum(1 for word in question.lower().split() if word in result[0].lower().split())
        if match_count > max_match_count:
            max_match_count = match_count
            closest_match = result[0]
    return closest_match

# Create a chatbot that can respond to customer queries
def chatbot():
    print("Welcome to Swiggy!")
    print("How may I help you?")
    while True:
        question = input("Customer: ")
        if question.lower() == "exit" or question.lower() == "stop" or question.lower() == "quit":
            print("Swiggy: Thank you for chatting with us! Goodbye!")
            break
        # Check if the question has been asked before
        answer = get_answer(question)
        if answer:
            print("Swiggy:", answer)
        else:
            # Generate a response to the question
            answer = generate_response(question)
            if answer:
                store_question_answer(question, answer)
                print("Swiggy:", answer)
            else:
                closest_match = find_closest_matching_question(question)
                if closest_match:
                    print("Swiggy: Did you mean '{}'?".format(closest_match))
                    response = input("Customer: ")
                    if response.lower() == "yes":
                        answer = get_answer(closest_match)
                        print("Swiggy:", answer)
                    elif response.lower() == "no":
                        print("Swiggy: I don't have that much information. I'm a beginner.")
                    else:
                        print("Swiggy: Sorry, I didn't understand that.")
                else:
                    print("Swiggy: I'm not able to answer this question.")

# Generate some frequent questions and their answers and add them to the chatbot database
frequent_questions = [
    ("What is the menu for today?", "Our menu for today includes a variety of delicious dishes."),
    ("What is the price of the dish?", "The price of the dish is Rs. 100."),
    ("How can I place an order?", "You can place an order by calling us at 1234567890 or by visiting our website."),
    ("What is your menu today?", "Our menu for today includes a variety of delicious dishes."),
    ("Menu for today", "Our menu for today includes a variety of delicious dishes."),
    ("Today's menu", "Our menu for today includes a variety of delicious dishes."),
    ("Can I get a discount?", "Yes, we offer a 10% discount on all orders above Rs. 500."),
    ("How long does delivery take?", "Delivery typically takes 30-45 minutes, depending on your location.")
]

for question, answer in frequent_questions:
    store_question_answer(question, answer)

# Start the chatbot
chatbot()

# Close the database connection
conn.close()
