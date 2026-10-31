from flask import Flask, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

# Load env file
load_dotenv()
print("Database selected:", os.getenv("DB_NAME"))
# Create Flask app instance
app = Flask(__name__)


# Create the database connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Create initial function for flask app
# Return results with GET request
@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM transactions LIMIT 10")
        transactions = cursor.fetchall()

        return jsonify(transactions)

    # Log any database query error
    except mysql.connector.Error:
        app.logger.exception("Database query failed")
        return jsonify({"error": "Database request failed"}), 500

    finally:
        # Close cursor object if created successfully and close connection 
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Run Flask server IF this specific file runs

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True, port=5050)
    