### Features:

# 1. User Authentication: 
   - Users can log in as customers or administrators by providing their email and password. After three failed login attempts, the account is automatically blocked.

# 2. Customer Functionality:
   - Customers can browse available items, view item details, and place orders.
   - The system tracks customer spending and provides insights into top-paying customers.

# 3. Administrator Functionality:
   - Administrators can analyze customer data, including total spending by customer.
   - Inventory management allows administrators to view available items

# 4. Database Triggers:
   - A trigger ensures that when an item's quantity is updated to 0, it automatically sets the quantity to 10.
   - Another trigger updates the login attempts counter for users before each login attempt. If the user exceeds three login attempts, their account is automatically blocked.

#  Code Structure:

# 1. Database Connectivity:
   - Establishes a connection to the MySQL database and initializes a cursor for executing SQL queries.

# 2. Triggers and Functions:
   - startingServer(): Initializes database triggers for updating login attempts and ensuring minimum item quantities.
   - loginsTrigger(): Updates the login attempts counter for users and blocks accounts if the login attempt limit is exceeded.

# 3. User Authentication:
   - Users can log in as customers or administrators. Failed login attempts are tracked, and accounts are blocked after three failures.

# 4. Customer and Administrator Functionality:
   - Customers can browse available items, place orders, and view order details.
   - Administrators can analyze customer data, analyze inventory

