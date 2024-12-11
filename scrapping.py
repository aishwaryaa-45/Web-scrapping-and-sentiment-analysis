import requests
from bs4 import BeautifulSoup
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

# Function to create the reviews table
def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title TEXT,
            review_text TEXT,
            style_name TEXT,
            color TEXT,
            verified_purchase BOOLEAN
        )
    """)
    print("Table 'reviews' is ready.")

# Function to scrape reviews from the page
def scrape_reviews(reviewurl,pg):
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/91.0.4472.124 Safari/537.36")
    }
    try:
        response = requests.get(reviewurl, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find_all("div", class_="review")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching reviews: {e}")
        return []

# Function to extract review details
def extract_review_data(review):
    try:
        title = review.find(["span", "a"], class_=[ "span","a-size-base"]).text.strip()
        review_text = review.find(["span","a"], class_="review-text").text.strip()

        
        

# Initialize default values
        color = "Black"
        style_name = "128GB"
        

        verified_purchase = "Verified Purchase" in review.text
        return title, review_text, style_name, color, verified_purchase
    except AttributeError as e:
        print(f"Error extracting review data: {e}")
        return None, None, None, None, None

# Main function to scrape and insert reviews into the database
def main():
    url =  "https://www.amazon.in/Apple-New-iPhone-12-128GB/dp/B08L5TNJHG/"
    pg = 1
    reviewurl = url.replace("dp", "product-reviews") + f"&pageNumber={pg}"
    conn = connect_to_db()
    if not conn:
        return

    cursor = conn.cursor()
    create_table(cursor)

    reviews = scrape_reviews(reviewurl,pg)
    if not reviews:
        print("No reviews found or failed to scrape reviews.")
        return

    for review in reviews:
        title, review_text, style_name, color, verified_purchase = extract_review_data(review)
        if title:  # Only insert if data is valid
            cursor.execute("""
                INSERT INTO reviews (title, review_text, style_name, color, verified_purchase)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, review_text, style_name, color, verified_purchase))
            conn.commit()

    print("Scraping and Data Insertion Completed!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

