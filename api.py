from flask import Flask, request, jsonify
from textblob import TextBlob  # Import TextBlob
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Function to initialize MySQL connection
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="Aish",
            user="root",
            password="Aishwaryaroot@29",
            database="reviews_db"
        )
        if conn.is_connected():
            print("Successfully connected to the database")
            return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Initialize connection
conn = connect_to_db()
if conn:
    cursor = conn.cursor(buffered = True)
else:
    raise Exception("Failed to connect to the database")

# Sentiment Analysis API
@app.route('/sentiment_label', methods=['POST'])
def sentiment_analysis():
    try:
        # Validate input
        if not request.json or 'review_text' not in request.json:
            return jsonify({"error": "Invalid request, 'review_text' field is required"}), 400
        
        # Get the review text from the request body
        review_text = request.json['review_text']
        
        # Perform sentiment analysis using TextBlob
        sentiment = TextBlob(review_text).sentiment.polarity
        
        # Classify sentiment as Positive, Negative, or Neutral
        sentiment_label = (
            "Positive" if sentiment > 0 else 
            "Negative" if sentiment < 0 else 
            "Neutral"
        )
        return jsonify({"sentiment": sentiment_label}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred during sentiment analysis: {str(e)}"}), 500

# Review Retrieval API
@app.route('/reviews', methods=['GET'])
def review_retrieval():
    try:
        # Get color and storage from query parameters
        id = request.args.get('id')
        title = request.args.get('title')
        review_text = request.args.get('review_text')
        style_name = request.args.get('style_name')
        color = request.args.get('color')
        verified_purchase = request.args.get('verified_purchase')
        sentiment_label = request.args.get('sentiment_label')
        
        
        # Fetch reviews from the database based on color and storage
        cursor.execute( """
            SELECT * FROM reviews WHERE 
            color = 'Black' and style_name = '128GB'
            """ )
        
        
        
        # Fetch all matching reviews
        reviews = cursor.fetchall()
        
        # If no reviews are found, return a message
        if not reviews:
            return jsonify({"message": "No reviews found for the specified criteria"}), 404
        
        # Prepare review data for returning
        review_list = []
        for review in reviews:
            review_list.append({
                "id": review[0],
                "title": review[1],
                "review_text": review[2],
                "style_name": review[3],
                "color": review[4],
                "verified_purchase": bool(review[5])
            })
        
        # Return the list of reviews
        return jsonify({"reviews": review_list}), 200

    except Error as e:
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Ensure the app runs only if executed directly
if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        # Close the database connection gracefully
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")
