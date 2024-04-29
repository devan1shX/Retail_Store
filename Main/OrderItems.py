import mysql.connector
from prettytable import PrettyTable

db = mysql.connector.connect(
    host="localhost",
    user="anish",
    passwd="Anish123@",
    database="dbms"
)

mycursor = db.cursor()

def items_list():
    print("\nITEMS AVAILABLE TO ORDER: \n")
    mycursor.execute('SELECT item_id, item_name, review, quantity, amount FROM item')
    result = mycursor.fetchall()

    table = PrettyTable()
    table.field_names = ["ID", "Item Name", "Review", "Quantity", "Amount"]

    for row in result:
        item_id, item_name, review, quantity, amount = row
        review = review[:30] if len(review) > 30 else review
        table.add_row([item_id, item_name, review, quantity, amount])

    print(table)

def order_items(input_list):
    userMoney = input_list[6]
    userId = input_list[0]
    item_no = -1
    quantity = 0
    while True:
        try:
            item_no = int(input("\nEnter item ID to order: "))
            quantity = int(input("Enter quantity to order: "))
        except ValueError:
            print("You have either entered Wrong format or we dont have that item_id available")
            continue

        mycursor.execute("SELECT max(item_id) FROM item")
        total_items = mycursor.fetchone()[0]

        if 1 <= item_no <= total_items:
            break
        else:
            print(f"Enter a valid choice (1 to {total_items})")

    if item_no != -1:

        mycursor.execute("SELECT amount FROM item WHERE item_id = %s", (item_no,))
        item_amount = mycursor.fetchone()[0]

        mycursor.execute("SELECT quantity FROM item WHERE item_id = %s", (item_no,))
        total_quantity = mycursor.fetchone()[0]

        if quantity <= total_quantity:

            total_cost = quantity * item_amount

            if total_cost <= userMoney:

                # 1) decrease quantity from item table
                new_quantity = total_quantity - quantity
                mycursor.execute("UPDATE item SET quantity = %s WHERE item_id = %s", (new_quantity, item_no))
                db.commit()

                # 2) decrease user's money
                new_userMoney = userMoney - total_cost
                mycursor.execute("UPDATE user SET amount = %s WHERE cust_id = %s", (new_userMoney, userId))
                db.commit()

                # 3) adding payment in payment table
                mycursor.execute("SELECT admin_id FROM item WHERE item_id = %s", (item_no,))
                adminID = mycursor.fetchone()[0]
                mycursor.execute("INSERT INTO payment (cust_id, admin_id, amount) VALUES (%s, %s, %s)", (userId, adminID, total_cost))
                db.commit()

                # 4) adding payment Method
                mycursor.execute("SELECT max(payment_id) FROM payment")
                paymentID = mycursor.fetchone()[0]
                method = input("Enter payment Method: ")
                mycursor.execute("INSERT INTO payment_method (payment_id, method) VALUES (%s, %s)", (paymentID, method,))
                db.commit()

                # 5) adding the entry in delivery table
                mycursor.execute("INSERT INTO delivery (cust_id, admin_id, item_id, payment_id, total_amount, quantity, delivery_status, delivery_date) VALUES (%s, %s, %s, %s, %s, %s, 'Commands Delivery', '2024-11-11')", (userId, adminID, item_no, paymentID, total_cost, total_quantity))
                db.commit()

                print("\nTotal amount paid: ",total_cost)
                print("Order placed successfully !!")
            
            else:
                print("\nInsufficient Funds !!")
        else:
            print("\nWe dont have that much quantity !!")


def adminFunctionalities(lst):
    print("\n1) Customer's Analysis")
    print("2) Inventory Analysis")
    
    while True:
        choice = input("\nEnter your choice: ")
        
        if choice.isdigit():
            choice = int(choice)
            if choice in range(1, 3):
                break
            else:
                print("Enter a valid choice (1 or 2)")
        else:
            print("Enter a valid choice (1 or 2)")
    
    if choice == 1:
        print("\nUser's who have paid so much and ordered many products : \n")
        mycursor.execute("""
        SELECT d.cust_id AS CUSTOMER_ID, CONCAT(u.fname, ' ', u.lname) AS CUSTOMER_NAME, 
        SUM(d.total_amount) AS TOTAL_PAID 
        FROM delivery AS d 
        INNER JOIN user AS u ON d.cust_id = u.cust_id 
        WHERE d.admin_id = %s
        GROUP BY CUSTOMER_ID, CUSTOMER_NAME 
        ORDER BY TOTAL_PAID DESC;
    """, (lst[0],))

        records = mycursor.fetchall()

        table = PrettyTable()
        table.field_names = ["CUSTOMER ID", "CUSTOMER NAME", "TOTAL PAID"]

        for record in records:
            table.add_row(record)

        print(table)
    elif choice == 2:
        mycursor.execute("SELECT item_id, item_name, quantity, amount, review FROM item WHERE admin_id = %s", (lst[0],))
        records = mycursor.fetchall()

        table = PrettyTable()
        table.field_names = ["ID", "NAME", "QUANTITY LEFT", "AMOUNT", "REVIEW"]

        for record in records:
            table.add_row(record)

        print(table)


def loginsTrigger(logins, userID, status):
    mycursor.execute("UPDATE user SET logins = %s WHERE cust_id = %s", (logins, userID))
    db.commit()



def startingServer():
    try:
        mycursor.execute("DROP TRIGGER IF EXISTS logins_trigger")

        mycursor.execute("DROP TRIGGER IF EXISTS add_items")

        mycursor.execute("SET SQL_SAFE_UPDATES = 0")

        mycursor.execute("UPDATE user SET logins = 0")

        mycursor.execute("UPDATE user SET account_status = %s", ('working',))

        mycursor.execute("""
            CREATE TRIGGER logins_trigger BEFORE UPDATE ON user
            FOR EACH ROW
            BEGIN
                SET NEW.logins = OLD.logins + 1;
            END;
        """)

        mycursor.execute(""" 
            CREATE TRIGGER add_items
            BEFORE UPDATE
            ON item FOR EACH ROW
            BEGIN
                IF NEW.quantity = 0 THEN
                    SET NEW.quantity = 10;
                END IF;
            END;
             """)

        db.commit()
    except Exception as e:
        print("An error occurred while starting the server:", e)



startingServer()


print("\n1) Enter as USER")
print("2) Enter as ADMIN")

while True:
    choice = input("\nEnter your choice: ")
    
    if choice.isdigit():
        choice = int(choice)
        if choice in range(1, 3):
            break
        else:
            print("Enter a valid choice (1 or 2)")
    else:
        print("Enter a valid choice (1 or 2)")

if choice == 1:
    userloginCount = 0
    userExists = False

    while userloginCount < 3:
        mail = input("\nEnter your email: ")
        passw = input("Enter your password: ")

        query = "SELECT * FROM user WHERE email = %s"

        id = -1

        mycursor.execute(query, (mail,))

        lst = []

        result = mycursor.fetchall()
        if len(result) > 0:
            for row in result:
                for attribute in row:
                    lst.append(attribute)
                    userExists = True
        else:
            print("\nNo user found with the provided email.")
            continue

        if len(lst) > 0 and passw != lst[5]:
            print("\nWrong pass")
            loginsTrigger(lst[12], lst[0], lst[13])
            
            userloginCount += 1
        else:
            break

    if userloginCount == 3:
        print("\nYour account has been blocked !!")
        mycursor.execute("UPDATE user SET account_status = %s WHERE cust_id = %s", ('BLOCKED', lst[0]))
        db.commit()
    elif userExists:
        print("\nHello, Welcome to the grocery store as USER!!")
        items_list()
        order_items(lst)

elif choice == 2:
    adminloginCount = 0
    adminExists = False

    while adminloginCount < 3:
        mail = input("\nEnter your email: ")
        passw = input("Enter your password: ")

        query = "SELECT * FROM admin WHERE email = %s"

        id = -1

        mycursor.execute(query, (mail,))

        lst = []

        result = mycursor.fetchall()
        if len(result) > 0:
            for row in result:
                for attribute in row:
                    lst.append(attribute)
                    adminExists = True
        else:
            print("\nNo user found with the provided email.")
            adminloginCount += 1
            continue

        if len(lst) > 0 and passw != lst[5]:
            print("\nWrong pass")
            adminloginCount += 1
        else:
            break

    if adminloginCount == 3:
        print("\nYour account has been blocked !!")
    elif adminExists:
        print("\nHello, Welcome to the grocery store as ADMIN !!")

    adminFunctionalities(lst)


db.close()
