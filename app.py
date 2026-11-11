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

# Sort options
sorting_options = {
    "platform": "platform",
    "model": "model",
    "unique_id": "unique_id",
    "input_tokens": "input_tokens",
    "input_cost": "input_cost",
    "output_tokens": "output_tokens",
    "output_cost": "output_cost",
    "total_cost" : "total_cost"
}

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

        # Sort request
        sort_by = request.args.get("sort_by")
        order = request.args.get("order", "asc").lower()

        if sort_by:
            if sort_by not in sorting_options:
                return jsonify({"error": "Invalid sorting option"}), 400
            if order not in ("asc", "desc"):
                return jsonify({"error": "Order must be ascending or descending"}), 400

            column = sorting_options[sort_by]

            query += f" ORDER BY `{column}` {order.upper()}"

            # Break ties using the unique transaction number
            if column != "transaction_number":
                query += ", `transaction_number` ASC"

        else:
            # Default sorting when no sort_by is provided
            query += " ORDER BY `transaction_number` ASC"

        limit_raw = request.args.get("limit", "20")
        page_raw = request.args.get("page", "1")

        try:
            limit = int(limit_raw)
            page = int(page_raw)
        except ValueError:
            return jsonify({"error": "Invalid pagination parameters"}), 400

        # Validate pagination parameters
        if limit is None or not 1 <= limit <= 100:
            return jsonify({"error": "Limit must be between 1 and 100"}), 400
        if page is None or page < 1:
            return jsonify({"error": "Page must be 1 or greater"}), 400

        offset = (page - 1) * limit

        # Add pagination to query
        query += " LIMIT %s OFFSET %s"
        values.extend([limit, offset])

        print("Page:", page)
        print("SQL query:", query)
        print("Values:", values)

        # Execute the query
        cursor.execute(query, tuple(values))
        transactions = cursor.fetchall()
        return jsonify(transactions)
        
    # Log any database query error
    except mysql.connector.Error:
        app.logger.exception("Database query failed")
        return jsonify({"error": "Database request failed"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# Run Flask server IF this specific file runs
if __name__ == "__main__":
    app.run(debug=True, port=5001)
