# from fastapi import FastAPI, Request
# import db_help
# from fastapi.responses import JSONResponse

# app = FastAPI()

# inprogress_orders = {}

# @app.get("/")
# async def root():
#     return {"message": "Server is running. Use POST to send data."}

# @app.post("/webhook")
# async def webhook(request: Request):
#     body = await request.json()  # Get the request body as JSON
#     print(body)  # Log the request payload to see if `order_id` is there

#     # Process the order_id
#     parameters = body['queryResult']['parameters']
#     order_id = parameters.get('number', None)

#     if not order_id:
#         return {"fulfillmentText": "Order ID is missing or invalid."}
    
#     try:
#         # Convert order_id to integer (even if it's a float like 41.0)
#         order_id = int(order_id)
#     except ValueError:
#         return {"fulfillmentText": "Order ID must be a number."}
    
#     # Fetch the order status from the database
#     order_status = db_help.get_order_status(order_id)

#     if order_status:
#         fulfillment_text = f"The order status for order ID {order_id} is: {order_status}"
#     else:
#         fulfillment_text = f"No order found with order ID {order_id}"

#     return {"fulfillmentText": fulfillment_text}

#     intent_handler_dict = {
#         'order.add - context: ongoing-order': add_to_order,
#         # 'order.remove - context: ongoing-order': remove_from_order,
#         # 'order.complete - context: Ongoing-order': complete_order,
#         'track.order- context: ongoing-order': track_order
#     }

#     return intent_handler_dict[intent](parameters)

# def add_to_order(parameters: dict):
#     food_items = parameters['food-item']
#     number = parameters['number']

#     if len(food_items) != len(number):
#         fulfillment_text = "Sorry I didn't understand can you specify food items and quantities clearly!"
#     else:
#         fulfillment_text = f"Received {food_items} and {number} in the backend"

#     return JSONResponse(content={
#         "fulfillmentText": fulfillment_text
#     })

# from fastapi import FastAPI
# from fastapi import Request
# from fastapi.responses import JSONResponse
# import db_help
# import generic_helper

# app = FastAPI()

# # Define the functions before referencing them
# def add_to_order(parameters: dict, session_id: str):
#     # Print the parameters to verify if 'food-item' and 'quantities' are present
#     print("Food Item:", parameters.get('food-item'))
#     print("Quantities:", parameters.get('quantities'))

#     # Extract food items and quantities
#     food_items = parameters.get('food-item', [])
#     quantities = parameters.get('quantities', [])

#     # Validate the parameters and prepare the response
#     if len(food_items) != len(quantities):
#         fulfillment_text = "Sorry, I didn't understand. Can you specify food items and quantities clearly?"
#     else:
#         new_food_dict = dict(zip(food_items, quantities)) 

#         if session_id in inprogress_orders:
#             current_food_dict = inprogress_orders[session_id]
#             current_food_dict.update(new_food_dict)
#             inprogress_orders[session_id] = current_food_dict
#         else:
#             inprogress_orders[session_id] = new_food_dict
        
#         order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
#         fulfillment_text = f"So far you have: {order_str}. Do you need anythinng else?"

#     return JSONResponse(content={"fulfillmentText": fulfillment_text})

# def track_order(parameters: dict):
#     order_id = parameters.get('order_id', None)

#     if order_id is None:
#         return JSONResponse(content={"fulfillmentText": "Order ID is missing or invalid."})
#     try:
#         # Convert order_id to integer
#         order_id = int(order_id)
#     except ValueError:
#         return JSONResponse(content={"fulfillmentText": "Order ID must be a number."})

#     # Fetch the order status from the database
#     order_status = db_help.get_order_status(order_id)

#     if order_status:
#         fulfillment_text = f"The order status for order ID {order_id} is: {order_status}"
#     else:
#         fulfillment_text = f"No order found with order ID {order_id}"

#     return JSONResponse(content={"fulfillmentText": fulfillment_text})
# session_id = generic_helper.extraact_session_id(output_context[0]['name'])
    

# # Define intent handler dictionary after function definitions
# intent_handler_dict = {
#     'order.add - context: ongoing-order': add_to_order,
#     'track.order- context: ongoing-order': track_order,
# }

# @app.post("/webhook")
# async def webhook(request: Request):
#     body = await request.json()  # Get the request body as JSON
#     print("Request Body:", body)  # Log the full request payload

#     # Extract intent and parameters from the body
#     intent = body.get('queryResult', {}).get('intent', {}).get('displayName')
#     parameters = body.get('queryResult', {}).get('parameters', {})

#     print("Extracted Intent:", intent)  # Log the extracted intent
#     print("Extracted Parameters:", parameters)  # Log the parameters
#     print("Extracted session_id:", session_id)

#     # Check if the intent exists in the handler dictionary
#     if intent in intent_handler_dict:
#         return intent_handler_dict[intent](parameters, session_id)
#     else:
#         return JSONResponse(content={"fulfillmentText": "Sorry, I didn't understand the intent."})

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import db_help
import generic_helper

app = FastAPI()

# In-memory dictionary to store in-progress orders (this can be replaced with a database)
inprogress_orders = {}

# Define the functions before referencing them
def add_to_order(parameters: dict, session_id: str):
    # Extract food items and quantities
    food_items = parameters.get('food-items', [])
    quantities = parameters.get('number', [])

    # Debugging: Print the extracted values
    print("Food Items:", food_items)
    print("Quantities:", quantities)

    # If the number of food items is less than the number of quantities
    if len(food_items) == 1 and len(quantities) > 1:
        # Repeat the food item to match the number of quantities
        food_items = [food_items[0]] * len(quantities)
    elif len(food_items) < len(quantities):
        # If we have fewer food items than quantities, repeat food items
        food_items = food_items * (len(quantities) // len(food_items)) + food_items[:len(quantities) % len(food_items)]

    # Handle case where food items are more than quantities
    if len(quantities) == 1 and len(food_items) > 1:
        # Repeat the quantity for each food item
        quantities = [quantities[0]] * len(food_items)

    # Ensure the lengths of food items and quantities match
    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, the number of food items and quantities do not match. Please try again."
    else:
        # Combine food items and quantities into a dictionary
        new_food_dict = dict(zip(food_items, quantities))

        # Update the inprogress_orders dictionary with the new food items for the session
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        # Generate the string representation of the current order
        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def complete_order(parameters: dict, session_id: str):
    # Check if the session has an in-progress order
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you please place the order again?"
    else:
        # Retrieve the order from the in-progress orders
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        # Handle errors in saving the order
        if order_id == -1:
            fulfillment_text = "I'm having trouble saving your order. Sorry! Can you please place the order again?"
        else:
            # Fetch the total order price from the database
            order_total = db_help.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We have placed your order. " \
                f"Here is your order id # {order_id}. " \
                f"Your order total is {order_total} which you can pay at the time of delivery!"
            
        # Remove the order from the in-progress orders after completing it
        del inprogress_orders[session_id]
    
    # Return the response in the correct format
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def save_to_db(order: dict):
    for food_item, quantity in order.items():
        item_id, price = db_help.get_item_details(food_item)
        if item_id is None or price is None:
            logging.error(f"❌ Failed to fetch item details for {food_item}")
            return -1

        logging.info(f"ℹ️ Inserting: item_id={item_id}, quantity={quantity}, total_price={price}")

        order_inserted = db_help.insert_order_to_orders(item_id, quantity, price)
        if not order_inserted:
            return -1

    return True  # Success




def track_order(parameters: dict):
    order_id = parameters.get('order_id', None)

    if order_id is None:
        return JSONResponse(content={"fulfillmentText": "Order ID is missing or invalid."})
    try:
        # Convert order_id to integer
        order_id = int(order_id)
    except ValueError:
        return JSONResponse(content={"fulfillmentText": "Order ID must be a number."})

    # Fetch the order status from the database
    order_status = db_help.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order ID {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order ID {order_id}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# Define intent handler dictionary after function definitions
intent_handler_dict = {
    'order.add - context: ongoing-order': add_to_order,
    'track.order- context: ongoing-order': track_order,
    'order.complete - context: Ongoing-order': complete_order,
}

from fastapi import FastAPI, Request, JSONResponse
import db_help
import generic_helper

app = FastAPI()

# Add a handler for the root path to prevent the 404 error
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Food Chatbot API"}

# Your existing webhook route
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()  # Get the request body as JSON
    print("Request Body:", body)  # Log the full request payload

    # Extract intent and parameters from the body
    intent = body.get('queryResult', {}).get('intent', {}).get('displayName')
    parameters = body.get('queryResult', {}).get('parameters', {})

    # Extract session_id from the request body using the session string
    session_str = body.get('session', '')  # Get session from the request body
    session_id = generic_helper.extraact_session_id(session_str)

    print("Extracted Intent:", intent)  # Log the extracted intent
    print("Extracted Parameters:", parameters)  # Log the parameters
    print("Extracted session_id:", session_id)

    # Check if the intent exists in the handler dictionary
    if intent in intent_handler_dict:
        return intent_handler_dict[intent](parameters, session_id)
    else:
        return JSONResponse(content={"fulfillmentText": "Sorry, I didn't understand the intent."})


