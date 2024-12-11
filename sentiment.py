from collections import Counter
from textblob import TextBlob
import mysql.connector
from mysql.connector import Error

# Function to connect to the database
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
        print(f"Error connecting to database: {e}")
        return None

# Function to fetch all reviews from the database
def fetch_reviews(cursor):
    cursor.execute("SELECT review_text FROM reviews")
    return [item[0] for item in cursor.fetchall()]

# Function to calculate and display word frequency
def analyze_word_frequency(reviews):
    word_freq = Counter(" ".join(reviews).split())
    print("Most Frequent Words:", word_freq.most_common(10))
    print("Least Frequent Words:", word_freq.most_common()[:-10:-1])

# Function to ensure the 'sentiment_label' column exists in the table
def ensure_sentiment_column(cursor):
    cursor.execute("DESCRIBE reviews")
    columns = [column[0] for column in cursor.fetchall()]
    if "sentiment_label" not in columns:
        cursor.execute("ALTER TABLE reviews ADD COLUMN sentiment_label VARCHAR(10)")
        print("Added 'sentiment_label' column to the 'reviews' table.")

# Function to perform sentiment analysis and update the database
def perform_sentiment_analysis(cursor, conn):
    cursor.execute("SELECT id, review_text FROM reviews")
    reviews = cursor.fetchall()

    for review_id, review_text in reviews:
        try:
            sentiment = TextBlob(review_text).sentiment.polarity
            sentiment_label = (
                "Positive" if sentiment > 0 else 
                "Negative" if sentiment < 0 else 
                "Neutral"
            )
            cursor.execute("""
                UPDATE reviews SET sentiment_label = %s WHERE id = %s
            """, (sentiment_label, review_id))
        except Exception as e:
            print(f"Error processing review ID {review_id}: {e}")
    conn.commit()
    print("Sentiment Analysis Completed!")

# Main function to coordinate the analysis
def main():
    conn = connect_to_db()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # Analyze word frequency
        reviews = fetch_reviews(cursor)
        if reviews:
            print("Performing Word Frequency Analysis...")
            analyze_word_frequency(reviews)
        else:
            print("No reviews found for word frequency analysis.")

        # Perform sentiment analysis
        print("Performing Sentiment Analysis...")
        ensure_sentiment_column(cursor)
        perform_sentiment_analysis(cursor, conn)

    except Error as e:
        print(f"Error during analysis: {e}")

    finally:
        cursor.close()
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
