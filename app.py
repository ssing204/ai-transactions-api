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


# Create filter list
allowed_filters = {
    "platform": "platform",
    "company": "company",
    "user": "user_number",
    "model": "model",
    "unique_id": "unique_id"
}


# Create initial function for flask app
# Return results with GET request
@app.route("/api/transactions", methods=["GET"])
def get_transactions():

    connection = None
    cursor = None

    try:
        # Establish connection to MySQL db
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Base SQL Query
        query = "SELECT * FROM transactions"
        conditions = []
        values = []

        # Loop through filter
        for param, column in allowed_filters.items():

            # Read the parameter from the URL
            value = request.args.get(param)

            if value is not None and value != "":
                conditions.append(f"`{column}` = %s")
                values.append(value)

        # Add WHERE conditions if filters exist
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Read the limit from the URL
        limit_raw = request.args.get("limit")

        if limit_raw is not None:
            try:
                limit = int(limit_raw)
            except ValueError:
                return jsonify({"error": "Limit must be an integer"}), 400

            # Validate requested limit
            if not 1 <= limit <= 100:
                return jsonify({
                    "error": "Limit must be between 1 and 100"
                }), 400

            # Add LIMIT clause to SQL query
            query += " LIMIT %s"
            values.append(limit)

        # 6. Execute the query
        cursor.execute(query, tuple(values))

        # 7. Retrieve the results
        transactions = cursor.fetchall()

        # 8. Return results as JSON
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
