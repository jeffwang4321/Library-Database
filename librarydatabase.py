# librarydatabase.py - Jeff Wang - 301309384 - CMPT354
# cd mnt/c/users/17789/desktop/mp

# python3 librarydatabase.py

import sqlite3
from datetime import timedelta, date, datetime
from prettytable import PrettyTable

# Helper function - Print all books
def showItems(conn):  
    print("\n>>>Listing All Books:")
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Item")
        rows=cur.fetchall()
        
        t = PrettyTable(['Item ID', 'Title', 'Author', 'Edition', 'Year', 'Genre', 'Total', 'Available'])

        # Show User all items
        for row in rows:
            t.add_row([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])

        print(t, "\n")


# Helper function - SELECT Person ID
def checkPersonID(conn, ID):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT ID FROM Person")
        rows = cur.fetchall()
        for row in rows:
            if(row[0] == ID): 
                return True
        return False


# Helper function - Check user entered a valid ID
def userInputID(conn):
    while True: 
        try:
            personID = int(input("Enter your ID: "))
        except ValueError:
            print("Not a number! Try again.")
            continue
        if (checkPersonID(conn, personID)):
            break
        else: 
            print("Not a valid ID! Try again.")
    return personID

    

# Helper function - SELECT Event ID
def checkEventID(conn, ID):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT ID FROM Event WHERE ID = " + str(ID))
        if(cur.fetchall()): 
            return True
        return False
    


# Helper function - Select * FROM ItemCopy ID
def checkItemCopy(conn, itemID, copyID):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ItemCopy WHERE itemID = " +str(itemID) + " AND copyNum = " + str(copyID))
        if(cur.fetchall()): 
            return True
        return False
    
    
    
# Helper function - Select itemID, copyNum, status FROM ItemCopy ID
def isItemCopyAvailable(conn, itemID, copyID):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT itemID, copyNum, status FROM ItemCopy WHERE itemID = " +str(itemID) + " AND copyNum = " + str(copyID))
        if(cur.fetchall()[0][2] == 'Available'): 
            return True
        return False    
    

        
# Helper function - SELECT ID FROM Item WHERE title = title AND author = author
def getItemID(conn, title, author):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT ID FROM Item WHERE title='" + title + "' AND author='" + author + "'")
        rows=cur.fetchall()
        if rows: 
            return rows[0][0]
        return None

        

# Helper function - SELECT * FROM CheckedOut WHERE itemID = itemID AND personID = personID AND copyID = copyID
def isItemCheckedOut(conn, itemID, personID, copyID):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CheckedOut WHERE itemID = " + str(itemID) + " AND personID = " + str(personID) + " AND copyID = " + str(copyID))
        if(cur.fetchall()): 
            return True
        return False  

    
    
# Helper function - SELECT * FROM CheckedOut WHERE personID = personID
def hasPersonCheckedOut(conn, personID):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CheckedOut WHERE personID = " + str(personID))
        if(cur.fetchall()): 
            return True
        return False  
    
 
    
# Helper function - Calculate the user's fine depending on the # of overdue days
def calculateFine(conn, itemID, personID, copyID):
    dueDate = ''
    fine = 0
    today = datetime.strptime(str(date.today()), '%Y-%m-%d')
    
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT dueDate FROM Dues WHERE itemID = " + str(itemID) + " AND personID = " + str(personID) + " AND copyID = " + str(copyID))
        result = cur.fetchall()
        if(result): 
            dueDate = datetime.strptime(result[0][0], '%Y-%m-%d')
        else: 
            return
        
        fine = (today-dueDate).days
        if(fine <= 0): 
            return 0
        else: 
            return fine
        

# Helper function - Find book with itemTitle, print row
def itemSearch(conn):    
    print("\n>>>Find item")
    itemSearch = str(input("Enter Title: "))
    
    with conn:
        cur = conn.cursor()
        myQuery = "SELECT * FROM Item WHERE title=:itemTitle"
        cur.execute(myQuery,{"itemTitle":itemSearch})
        rows=cur.fetchall()
        
        if rows:
            print("\nWe have the following item/s with the title '" + itemSearch + "': ")
        else:
            print("\nUnfortunately, we do not have any items with the title '" + itemSearch + "'\n")

        t = PrettyTable(['Item ID', 'Title', 'Author', 'Edition', 'Year', 'Genre', 'Total', 'Available'])

        for row in rows:
            t.add_row([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
        print(t, "\n")


# Helper function - Checkout book with itemID and copyID
def itemCheckout(conn):
    print("\n>>>Checkout Item")
    personID = userInputID(conn)
    itemID = None
    copyID = None
    
    # Check if itemID and copyID is valid and available
    while True: 
        try:
            itemID = int(input("Enter item ID located in the back of the book: "))
            copyID =  int(input("Enter copy ID located in the back of the book: "))
        except ValueError:
            print("Not a number! Try again.")
            continue
        if (checkItemCopy(conn, itemID, copyID)):
            if (isItemCopyAvailable(conn, itemID, copyID)):
                break
            else:
                print("That copy is unavailable, try again.\n")
        else: 
            print("Not a valid ID! Try again.")
    
    with conn:
        cur = conn.cursor()
        
        # User has 3 weeks until they have to return the item without fines
        dueDate = date.today() + timedelta(days=21)
        
        # Insert to CheckedOut and Dues in Library.db
        cur.execute("INSERT INTO Dues (itemID, personID, copyID, dueDate) VALUES (" + str(itemID) + ", " + str(personID) + ", " + str(copyID) + ", '" + str(dueDate) + "')")
        cur.execute("INSERT INTO CheckedOut (itemID, personID, copyID) VALUES (" + str(itemID) + ", " + str(personID) + ", " + str(copyID) + ")")
        cur.execute("SELECT numAvailable FROM Item WHERE ID = " + str(itemID))

        numAvailable = cur.fetchall()[0][0] - 1
        cur.execute("UPDATE Item SET numAvailable = " + str(numAvailable) + " WHERE ID = " + str(itemID) )
        cur.execute("UPDATE ItemCopy SET status = 'Not Available' WHERE itemID = " + str(itemID) + " AND copyNum = " + str(copyID))
        print("\nCheckout successful! Your item is due on " + str(dueDate)+ "\n")
    
    
# Helper function - Return book 
def itemReturn(conn):
    # add fines to owes
    print("\n>>>Return Item")
    personID = userInputID(conn)
    itemID = None
    copyID = None
    
    # Check if the person has a copy to return
    if(hasPersonCheckedOut(conn, personID) == False):
        print("You have not checked anything out. You have nothing to return.\n")
        return
    
    with conn:
        cur = conn.cursor()
        
        # Show user list of items and due dates 
        cur.execute("SELECT itemID, copyID, title, dueDate FROM Dues, Item WHERE" + " itemID = ID AND personID = " + str(personID))
        rows = cur.fetchall()
        print("\nYour checked out items and their due dates:")
        if rows:
            for row in rows:
                print("Item ID: " + str(row[0]) + ", copy ID: "+ str(row[1]) + ", title: " + row[2] + " is due on " + str(row[3]))
            print()

        # Check if item copy has been checked out
        while True: 
            try:
                itemID = int(input("Enter item ID located in the back of the book: "))
                copyID =  int(input("Enter copy ID located in the back of the book: "))
            except ValueError:
                print("Not a number! Try again.")
                continue
            if (isItemCheckedOut(conn, itemID, personID, copyID)):
                break
            else: 
                print("You have not checked out that copy. Try again.")
        
        # Delete from CheckedOut and Dues, Update copy's status, Update numAvailable for item
        # Calculate person's fines
        fine = calculateFine(conn, itemID, personID, copyID)
        cur.execute("DELETE FROM CheckedOut WHERE itemID = " + str(itemID) +" AND personID = " + str(personID) + " AND copyID = " + str(copyID))
        cur.execute("DELETE FROM Dues WHERE itemID = " + str(itemID) + " AND personID = " + str(personID) + " AND copyID = " + str(copyID))
        cur.execute("UPDATE ItemCopy SET status = 'Available' WHERE itemID = " + str(itemID) + " AND copyNum = " + str(copyID))
        cur.execute("SELECT numAvailable FROM Item WHERE ID = " + str(itemID))

        numAvailable = cur.fetchall()[0][0] + 1
        cur.execute("UPDATE Item SET numAvailable = " + str(numAvailable) + " WHERE ID = " + str(itemID))
        cur.execute("SELECT owes FROM Person WHERE ID = " + str(personID))
        owes = cur.fetchall()[0][0] + fine
        cur.execute("UPDATE Person SET owes = " + str(owes) + " WHERE ID = " + str(personID))
        
        print("Thanks for returning an item!\n")

    
# Helper function - Donate book (add book to DB) 
def itemDonation(conn):
    print("\n>>>Donate Item")
    print("Fill in all fields below (NULL if it is unknown)")
    
    # Begin user input and make sure "   " is not accepted
    while True:
        title = input("Title: ")
        if(title.isspace() or title == ""):
            print("Fill in the title field.")
        else: break
    while True:
        author = input("Author: ")
        if(author.isspace() or author == ""):
            print("Fill in the author field.")
        else: break
    while True:
        edition = input("Edition: ")
        if(edition.isspace() or edition == ""):
            print("Fill in the edition field.")
        else: break
    while True: # User only has two options for genre
        genre = input("Genre (FIC or NON FIC): ")
        if (genre == 'FIC' or genre == 'NON FIC'): break
        else:
            print("Input not valid! Try again.")
            continue
    while True: 
        try:
            year = int(input("Publication year: "))
        except ValueError:
            print("Not a number! Try again.")
            continue
        else:
            break
    # End of user input
    
    with conn:
        cur = conn.cursor()
        ID = getItemID(conn, title, author)

        # Add a copy if item is already in the system
        if (ID != None):
            cur.execute("SELECT quantity, numAvailable FROM Item WHERE ID =" + str(ID))
            result = cur.fetchall()
            copyNum = result[0][0] + 1
            numAvailable = result[0][1] + 1

            cur.execute("INSERT INTO ItemCopy (itemID, copyNum, type, status) VALUES (" + str(ID) + ", " + str(copyNum) + ", 'print', 'Available')")
            cur.execute("UPDATE Item SET quantity =" + str(copyNum) + ", numAvailable = " + str(numAvailable) + " WHERE ID = " + str(ID))
        
        # Add new item and add a copy if donation is not already in the library
        else:
            cur.execute("SELECT MAX(ID) FROM Item")
            ID = cur.fetchall()[0][0] + 1
            cur.execute("INSERT INTO Item (ID, title, author, edition, year, genre, " + "quantity, numAvailable) VALUES (" + str(ID) + ", '" + title + \
                        "', '" + author + "', '" + edition + "', " + str(year) + ", '" + genre + "', 1, 1)")
            cur.execute("INSERT INTO ItemCopy (itemID, copyNum, type, status) VALUES (" + str(ID) + ", 1, 'print', 'Available')")
        print("\nThank you for donating!\n")
    
    
# Helper function - Print all events
def showEvents(conn):  
    print("\n>>>Listing All Events:")
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Event")
        rows=cur.fetchall()
        
        t = PrettyTable(['Event ID', 'Event', 'Date', 'Room', 'Time', 'Fee', 'Recommended Age'])

        # Show User all events
        for row in rows:
            t.add_row([row[0], row[1], row[2], row[3], row[4] + '-' + row[5], row[6], row[7]])
        print(t, "\n")


# Helper function - Register for event using eventID
def eventRegistration(conn):
    print("\n>>>Event Registration:")
    
    with conn:
        cur = conn.cursor()
            
        try:
            personID = userInputID(conn)
            while True: 
                try:
                    eventID = int(input("Enter event ID: "))
                except ValueError:
                    print("Not a number! Try again.")
                    continue
                if (checkEventID(conn, eventID)):
                    break
                else: 
                    print("Not a valid ID! Try again.")        
           
            # Attempt to insert
            cur.execute("INSERT INTO Registered (personID, eventID) VALUES (" + \
                str(personID) + ", " + str(eventID) + ")")
        
        except sqlite3.IntegrityError:
            print("You are already registered into that event.\n")
            return
        else:    
            print("Registration Successful.\n")
    
    
# Helper function - Find event using eventName
def findEvent(conn):
    print("\n>>>Find Event")
    with conn:
        cur = conn.cursor()
        event= input("Enter event name: ")
        cur.execute("SELECT * FROM Event WHERE eventName = '" + event + "'")
        rows=cur.fetchall()
        
        if rows:
            print("\nWe have the following events with the name '" + event + "': ")
       
            t = PrettyTable(['Event ID', 'Event', 'Date', 'Room', 'Time', 'Fee', 'Recommended Age'])

            for row in rows:
                t.add_row([row[0], row[1], row[2], row[3], row[4] + '-' + row[5], row[6], row[7]])
            print(t, "\n")
            eventRegistration(conn)
            
        else:
            print("Unfortunately, we do not have any events with the name '" + event + "'\n")       
    
    
# Helper function - Add user as volunteer
def volunteer(conn):
    print("\n>>>Volunteer")
    
    # Begin user input
    print("Please enter your:")
    firstName = input("First name: ")
    lastName = input("Last name: ")
    while True: # Make sure age is a number
        try:
            age = int(input("Age: "))
        except ValueError:
            print("Not a number! Try again.")
            continue
        else:
            break
    while True: # User only has two options for gender
        gender = input("Gender (M or F): ")
        if (gender == 'M' or gender == 'F'): 
            break
        else:
            print("Input not valid! Try again.")
            continue
    # End of user input
            
    with conn:
        cur = conn.cursor()
        
        # Getting an id number for the volunteer
        cur.execute("SELECT MAX(ID) FROM Staff")
        ID = cur.fetchall()[0][0] + 1

        # Inserting user input to staff with the role as 'Volunteer'
        cur.execute("INSERT INTO Staff (ID, firstName, lastName, age, gender, role)" + "VALUES (" + str(ID) + ", '" + firstName + "', '" + lastName + "', '" + \
            str(age) + "', '" + gender + "', 'Volunteer')")
        
        print("\nThank you for signing up to be a volunteer. We will email you further details within 7 days\n")
    
    
# Helper function - Check if a librarian is available
def askLibrarian(conn):     
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT firstName FROM Staff WHERE role='Librarian'")
        rows=cur.fetchall()
        librarians = ''
        
        for row in rows:
            librarians += row[0] + ", "
        
        if rows:
            print("\nOne of " + librarians + "will be right with you.\n")
        else:
            print("\nUnfortunately, there are no available librarians at the moment.\n")


# Helper function - Check users due dates and fines         
def duesAndFines(conn):
    personID = userInputID(conn)
    
    with conn:
        cur = conn.cursor()
        fine = 0
        
        # Show user list of items and due dates 
        cur.execute("SELECT title, author, dueDate FROM Dues, Item WHERE itemID = ID AND personID = " + str(personID))
        rows = cur.fetchall()
        print("\nYour checked out items and their due dates:")
        if rows:
            for row in rows:
                print(row[0]+" by " + row[1] + " is due on " + row[2])
                
        # Show user amount owed
        cur.execute("SELECT itemID, personID, copyID FROM Dues WHERE personID = " + str(personID))
        rows = cur.fetchall()
        if rows:
            for row in rows:
                fine += calculateFine(conn, row[0], row[1], row[2])
        cur.execute("SELECT owes FROM Person WHERE ID = " + str(personID))
        owes = cur.fetchall()[0][0] + fine
        print("You owe the library $" + str(owes) + ".00\n")
            
   
# Helper function - Pay user's fines
def payFines(conn):
    personID = userInputID(conn)
    
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT owes FROM Person WHERE ID = " + str(personID))
        owes = cur.fetchall()[0][0]
        print("\nYou owe the library $" + str(owes) + ".00")
        print("Active fines with currently checked out books are not included.\n")
        
        if(owes == 0): return
        else:
            while True: # User can only pay amount <= owes
                pay = int(input("Pay amount: "))
                if (pay <= owes): 
                    break
                else:
                    print("You are overpaying. Try again.")
                    continue
            cur.execute("UPDATE Person SET owes = " + str(owes - pay) + " WHERE ID = " + str(personID))
            cur.execute("SELECT owes FROM Person WHERE ID = " + str(personID))
            owes = cur.fetchall()[0][0]
            print("You owe the library $" + str(owes) + ".00 after your payment\n")
        
        
# Helper function - Sign user up (add to people DB)
def signUp(conn):
    print("\n>>>Sign up")
    print("Fill in all fields below.")
    firstName = input("First name: ")
    lastName = input("Last name: ")
    while True: # Make sure age is a number
        try:
            age = int(input("Age: "))
        except ValueError:
            print("Not a number! Try again.")
            continue
        else:
            break
    
    # Insert new user to database of people
    with conn:
        cur = conn.cursor()
        
        # Getting an id number for the new user
        cur.execute("SELECT MAX(ID) FROM Person")
        ID = cur.fetchall()[0][0] + 1
        cur.execute("INSERT INTO Person (ID, firstName, lastName, age)" + "VALUES (" + str(ID) + ", '" + firstName + "', '" + lastName + "', " + str(age) + ")")
        print("Thank you for signing up. Enjoy the library!\n")
        

# Helper function - Print all books
def showPersons(conn):  
    print("\n>>>Listing All People and Dues:")
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Person")
        rows=cur.fetchall()

        cur.execute("SELECT * FROM Dues")
        rows2=cur.fetchall()

        t = PrettyTable(['Person ID', 'First Name', 'Last Name', 'Age', 'Owes'])
        t2 = PrettyTable(['Copy ID', 'Person ID', 'Item ID', 'Due Date'])
        
        # Show User all events
        for row in rows:
            t.add_row([row[0], row[1], row[2], row[3], row[4]])

        for row in rows2:
            t2.add_row([row[0], row[1], row[2], row[3]])
        
        print(t, "\n")
        print(t2, "\n")
        

# Display user actions, collects inputs and run fuction 
def userAction(conn):
    # User choices
    print("Please select from the following options:")
    print("\n0) List all items\n1) Find item\n2) Item checkout\n3) Item return\n4) Item donation\n5) List all events\n6) Find event\n" + \
          "7) Event registration\n8) Volunteer\n9) Ask a librarian\n10) Due dates and active fines\n11) Pay fines\n12) Sign up\n13) List all people and dues dates\n14) Shut Down\n")
    
    # Make sure user input is an integer
    while True:
        try:
            option = int(input("Option number: "))
        except ValueError:
            print("Not a number! Try again.")
            continue
        else:
            if(option < 0 or option > 14):
                print("Not a valid option! Try again.")
                continue
            break   
    
    if(option == 0): showItems(conn)
    if(option == 1): itemSearch(conn)
    if(option == 2): itemCheckout(conn)
    if(option == 3): itemReturn(conn)
    if(option == 4): itemDonation(conn)
    if(option == 5): showEvents(conn)
    if(option == 6): findEvent(conn)
    if(option == 7): eventRegistration(conn)
    if(option == 8): volunteer(conn)    
    if(option == 9): askLibrarian(conn)
    if(option == 10): duesAndFines(conn)    
    if(option == 11): payFines(conn)    
    if(option == 12): signUp(conn)
    if(option == 13): showPersons(conn)
    if(option == 14): return

    userAction(conn)
    
    
    
def main():  
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    print("\nOpened database successfully \n")
    
    userAction(conn)

    if conn:
        conn.close()
        print("Closed database successfully\n")
    print("Thank you for visiting the library. Happy reading!")
        
if __name__ == '__main__':
    main()