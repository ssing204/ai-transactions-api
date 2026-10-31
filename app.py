from flask import Flask, jsonify, request
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

    # Initialize db connection and cursor variable
    connection = None
    cursor = None

    # Create platform filter
    platform = request.args.get("platform")

    try:
        # Establish connection to MySQL db
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if platform: 
            query = """
                SELECT * 
                FROM transactions
                WHERE Platform = %s
                LIMIT 10    
            """
            cursor.execute(query, (platform,))
        else: 
            cursor.execute("SELECT * FROM transactions LIMIT 10")
        transactions = cursor.fetchall()
        return jsonify(transactions)

    # Log any database query error
    except mysql.connector.Error:
        app.logger.exception("Database query failed")
        return jsonify({"error": "Database request failed"}), 500

    finally:
        # Close cursor object if created successfully and close connection 
        cursor.close()
        connection.close()


# Run Flask server IF this specific file runs

if __name__ == "__main__":
    app.run(debug=True, port=5001)
