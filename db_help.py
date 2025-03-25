import mysql.connector
import logging

# Global connection variable
cnx = None

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

def connect_to_db():
    global cnx
    if cnx is None or not cnx.is_connected():
        try:
            cnx = mysql.connector.connect(
                host="127.0.0.1",       # Replace with your database host
                user="root",            # Replace with your database username
                password="3436",        # Replace with your database password
                database="chatbot"      # Replace with your database name
            )
            logging.info("Database connection established.")
        except mysql.connector.Error as err:
            logging.error(f"Error: {err}")
            cnx = None  # Ensure cnx is set to None if the connection fails
            return None
    return cnx

def check_food_item_exists(food_item):
    cnx = connect_to_db()  # Ensure connection is established
    if cnx is None:
        return False  # If connection failed, return False

    cursor = cnx.cursor()  # Ensure cursor is created for this query
    query = "SELECT * FROM menu WHERE item_name = %s"
    cursor.execute(query, (food_item,))
    result = cursor.fetchall()
    cursor.close()  # Always close cursor after query execution
    
    # If result is not empty, return True; otherwise, return False
    return len(result) > 0

def get_item_details(food_item):
    cnx = connect_to_db()  # Ensure connection is established
    if cnx is None:
        return None  # If connection failed, return None

    cursor = cnx.cursor()  # Ensure cursor is created for this query
    query = "SELECT item_id, price FROM menu WHERE item_name = %s"
    cursor.execute(query, (food_item,))
    
    # Fetch the result and ensure we get a single item
    result = cursor.fetchone()  # Use fetchone instead of fetchall, to get one row
    
    # Close the cursor
    cursor.close()
    
    if result:
        # Return item_id and price if the food item exists
        return result  # result[0] -> item_id, result[1] -> price
    else:
        # Return None or raise an exception if the item is not found
        return None

# Function to close the connection and cursor
def close_db_connection():
    if cnx and cnx.is_connected():
        cnx.close()

def insert_order_to_orders(order_id, item_id, quantity, price, user_id):
    cnx = connect_to_db()  # Ensure the connection is established
    if cnx is None:
        return False  # If connection failed, return False
    
    cursor = cnx.cursor()
    try:
        query = """
            INSERT INTO orders (item_id, quantity, total_price) 
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        cursor.execute(query, (item_id, quantity, price))
        cnx.commit()  # Commit the transaction

        logging.info(f"✅ Order {order_id} inserted successfully!")
        return True  # Success

    except mysql.connector.Error as e:
        logging.error(f"❌ Error inserting order: {e}")
        cnx.rollback()  # Rollback on error
        return False  # Failure

    finally:
        cursor.close()

def insert_order_item(food_item, quantity, order_id):
    cnx = connect_to_db()  # Ensure connection is established
    if cnx is None:
        return -1  # If connection failed, return failure

    cursor = cnx.cursor()  # Ensure cursor is created for this query
    try:
        # Check if food item exists in the food_items table
        food_item_exists = check_food_item_exists(food_item)  # Call the function from db_help
        if not food_item_exists:
            raise ValueError(f"Food item '{food_item}' does not exist.")

        # Get item details (item_id and price)
        item_details = get_item_details(food_item)
        if item_details is None:
            raise ValueError(f"Food item '{food_item}' does not have valid details.")
        
        item_id, price = item_details

        # Insert the order item into the database
        query = "INSERT INTO order_items (order_id, item_id, quantity) VALUES (%s, %s, %s)"
        values = (order_id, item_id, quantity)
        cursor.execute(query, values)
        cnx.commit()
        return 1  # Success

    except Exception as e:
        logging.error(f"Error inserting order item: {e}")
        cnx.rollback()  # Rollback on error
        return -1  # Failure
    finally:
        cursor.close()  # Ensure cursor is always closed after execution

def get_total_order_price(order_id):
    cnx = connect_to_db()  # Ensure connection is established
    if cnx is None:
        return None  # If connection failed, return None

    cursor = cnx.cursor()  # Ensure cursor is created for this query
    try:
        # Using an f-string to inject the order_id into the SQL query
        query = f"SELECT get_total_order_price({order_id})"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]
        return result
    finally:
        cursor.close()  # Ensure cursor is always closed after execution

def get_next_order_id():
    cnx = connect_to_db()  # Ensure connection is established
    if cnx is None:
        return None  # If connection failed, return None

    cursor = cnx.cursor()  # Ensure cursor is created for this query
    try:
        # Executing the SQL query to get the next available order_id
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Returning the next available order_id
        return 1 if result is None else result + 1
    finally:
        cursor.close()  # Ensure cursor is always closed after execution

def insert_order_tracking(order_id, status):
    cnx = connect_to_db()  # Ensure connection is established
    if cnx is None:
        return False  # If connection failed, return False

    cursor = cnx.cursor()  # Ensure cursor is created for this query
    try:
        # Inserting the record into the order_tracking table
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        cnx.commit()
        return True
    finally:
        cursor.close()  # Ensure cursor is always closed after execution

def get_order_status(order_id: int):
    cnx = connect_to_db()  # Ensure connection is established
    if cnx is None:
        return "❌ Database connection failed!"  # If connection failed, return error message

    cursor = cnx.cursor()  # Ensure cursor is created for this query
    try:
        # Executing the SQL query to fetch the order status
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))

        # Fetching the result
        result = cursor.fetchone()

        # Returning the order status
        if result is not None:
            return result[0]
        else:
            return "⚠️ Order ID not found!"
    except mysql.connector.Error as err:
        logging.error(f"Database Error: {err}")
        return f"❌ Database Error: {err}"
    finally:
        cursor.close()  # Ensure cursor is always closed after execution
