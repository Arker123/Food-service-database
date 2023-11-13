# Program for managing stock in medical store

import os
import sys
import time
import hashlib
from datetime import date

import MySQLdb

from config import Credentials

profit_margin = 0.20  # 20% profit margin

mydb = MySQLdb.connect(Credentials.host, Credentials.username, Credentials.password)

c = mydb.cursor()

# Create database if doesn't exist
try:
    c.execute("create database {}".format(Credentials.database))
except:
    pass

# Use the database
c.execute("use {}".format(Credentials.database))

# Create the raw table relations if it doesn't exist
try:
    c.execute(
        "create table Raw_materials(Material_id integer primary key AUTO_INCREMENT, Name varchar(25), Price integer(10),Expiry_date date, Seller_id integer)"
    )
    mydb.commit()
except:
    pass

# Create the Recipes relations if it doesn't exist
try:
    c.execute(
        "create table Recipes(Recipe_id integer primary key, Name varchar(25), Cost_Price integer(10), Selling_price integer(10), Availaible Tinyint(1))"
    )
    mydb.commit()
except:
    pass

# Create the Recipe_items relations if it doesn't exist
try:
    c.execute(
        "create table Recipe_items(Recipe_id integer primary key, Material_id integer, Quantity_required integer(10))"
    )
    mydb.commit()
except:
    pass

# Create the Seller_info relations if it doesn't exist
try:
    c.execute(
        "create table Seller_info(Seller_id integer primary key, name varchar(25), contact BIGINT, email varchar(25))"
    )
    mydb.commit()
except:
    pass

# Create the Seller_sold relations if it doesn't exist
try:
    c.execute("create table Seller_sold(Seller_id integer primary key, date_sold date, Material_id integer)")
    mydb.commit()
except:
    pass

# Create the Seller_sold relations if it doesn't exist
try:
    c.execute(
        "create table Customer_info(Customer_id integer primary key, name varchar(25), contact integer(30), email varchar(25), age integer(8), gender varchar(1))"
    )
    mydb.commit()
except:
    pass

# Create the Sales relations if it doesn't exist
try:
    c.execute(
        "create table Sales(Customer_id integer primary key, date_purchased date, Recipe_id integer, amount_paid integer)"
    )
    mydb.commit()
except:
    pass


def menu():
    print("1. Add new Raw material")
    print("2. Add new Recipe")
    print("3. Add new Seller")
    print("4. Add new Customer")
    print("5. Sell a recipe")
    print("6. Show food menu")
    print("7. Show raw materials")
    print("8. Show recipes")
    print("9. Show sellers")
    print("10. Show customers")
    print("11. Show sales")
    print("12. Exit")


def showRawMaterials():
    query = "select * from Raw_materials"
    c.execute(query)
    rows = c.fetchall()
    print("Material_id\t\tName\t\tPrice\t\tExpiry_date\t\tSeller_id")
    for row in rows:
        print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(row[0], row[1], row[2], row[3], row[4]))


def showRecipes():
    query = "select * from Recipes"
    c.execute(query)
    rows = c.fetchall()
    print("Recipe_id\t\tName\t\tCost_Price\t\tSelling_price\t\tAvailaible")
    for row in rows:
        print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(row[0], row[1], row[2], row[3], row[4]))


def showSellers():
    query = "select * from Seller_info"
    c.execute(query)
    rows = c.fetchall()
    print("Seller_id\t\tName\t\tContact\t\tEmail")
    for row in rows:
        print("{}\t\t{}\t\t{}\t\t{}".format(row[0], row[1], row[2], row[3]))


def showCustomers():
    query = "select * from Customer_info"
    c.execute(query)
    rows = c.fetchall()
    print("Customer_id\t\tName\t\tContact\t\tEmail\t\tAge\t\tGender")
    for row in rows:
        print("{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}".format(row[0], row[1], row[2], row[3], row[4], row[5]))


def showSales():
    query = "select * from Sales"
    c.execute(query)
    rows = c.fetchall()
    print("Customer_id\t\tDate_purchased\t\tRecipe_id\t\tAmount_paid")
    for row in rows:
        print("{}\t\t{}\t\t{}\t\t{}".format(row[0], row[1], row[2], row[3]))


def addSeller():
    name = input("Enter the name of the seller: ")
    contact = int(input("Enter the contact number of the seller: "))
    email = input("Enter the email of the seller: ")

    # hash the contact (int) number and email
    seller_id = int(hashlib.sha256(str(contact).encode("utf-8")).hexdigest(), 16) % 10**8

    query = "insert into Seller_info(Seller_id, name, contact, email) values({}, '{}', {}, '{}')".format(
        seller_id, name, contact, email
    )
    c.execute(query)
    mydb.commit()
    print("Seller added successfully")


def addRecipe():
    name = input("Enter the name of the recipe: ")

    cost_price = 0
    selling_price = 0
    availaible = 0

    # insert raw materials required for the recipe
    while True:
        material_id = int(input("Enter the material id: "))
        quantity = int(input("Enter the quantity required: "))

        query = "insert into Recipe_items(Recipe_id, Material_id, Quantity_required) values({}, {}, {})".format(
            name, material_id, quantity
        )

        c.execute(query)
        mydb.commit()

        # calculate the cost price of the recipe
        query = "select Price from Raw_materials where Material_id={}".format(material_id)
        c.execute(query)
        rows = c.fetchall()
        cost_price += rows[0][0] * quantity

        selling_price += cost_price * (1 + profit_margin)

        # Calculate Availaibility
        query = "select Expiry_date from Raw_materials where Material_id={}".format(material_id)
        c.execute(query)
        rows = c.fetchall()
        today = date.today()
        if rows[0][0] > today:
            availaible = 1

        print("Material added successfully")
        choice = input("Do you want to add more materials? (y/n): ")
        if choice == "n":
            break

    query = "insert into Recipes(Name, Cost_Price, Selling_price, Availaible) values('{}', {}, {}, {})".format(
        name, cost_price, selling_price, availaible
    )
    c.execute(query)
    mydb.commit()
    print("Recipe added successfully")


def addRawMaterial(seller_id):
    name = input("Enter the name of the raw material: ")
    price = int(input("Enter the price of the raw material: "))
    expiry = input("Enter the expiry date of the raw material: ")

    query = "insert into Raw_materials(Name, Price, Expiry_date, Seller_id) values('{}', {}, '{}', {})".format(
        name, price, expiry, seller_id
    )
    c.execute(query)
    mydb.commit()
    print("Raw material added successfully")


def showFoodMenu():
    query = "select Name, Selling_price, Availaible from Recipes"
    c.execute(query)
    rows = c.fetchall()
    print("Name\t\tSelling Price\t\tAvailaible")
    for row in rows:
        print("{}\t\t{}\t\t{}".format(row[0], row[1], row[2]))


def sellRecipe():
    pass


def addCustomer():
    query = "select max(Customer_id) from Customer_info"
    c.execute(query)
    rows = c.fetchall()
    customer_id = rows[0][0] + 1

    name = input("Enter the name of the customer: ")
    contact = int(input("Enter the contact number of the customer: "))
    email = input("Enter the email of the customer: ")
    age = int(input("Enter the age of the customer: "))
    gender = input("Enter the gender of the customer: ")

    # query = "insert into Customer_info(Customer_id, name, contact, email, age, gender) values"


def verifySeller(seller_id):
    query = "select * from Seller_info where Seller_id={}".format(seller_id)
    c.execute(query)
    rows = c.fetchall()
    if len(rows) == 0:
        return False
    return True


def main():
    # Show the menu
    menu()

    # Get the choice
    choice = int(input("Enter your choice: "))
    if choice == 1:
        seller_id = int(input("Enter the seller id: "))
        if verifySeller(seller_id):
            while True:
                addRawMaterial(seller_id)
                choice = input("Do you want to add more materials? (y/n): ")
                if choice == "n":
                    break
        else:
            print("Seller not found")
            return

    elif choice == 2:
        addRecipe()
    elif choice == 3:
        addSeller()
    elif choice == 4:
        addCustomer()
    elif choice == 5:
        sellRecipe()
    elif choice == 6:
        showFoodMenu()
    elif choice == 7:
        showRawMaterials()
    elif choice == 8:
        showRecipes()
    elif choice == 9:
        showSellers()
    elif choice == 10:
        showCustomers()
    elif choice == 11:
        showSales()
    elif choice == 12:
        exit()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()


def insert_demo_items():
    query = "insert into Raw_materials(Name, Price, Expiry_date, Seller_id) values('Milk', 50, '2023-11-31', 12345678)"
    c.execute(query)
    mydb.commit()

    query = "insert into Raw_materials(Name, Price, Expiry_date, Seller_id) values('Sugar', 40, '2023-11-31', 12345678)"
    c.execute(query)
    mydb.commit()

    query = "insert into Raw_materials(Name, Price, Expiry_date, Seller_id) values('Tea', 20, '2023-11-31', 12345678)"
    c.execute(query)
    mydb.commit()

    query = "insert into Recipes(Name, Cost_Price, Selling_price, Availaible) values('Tea', 110, 132, 1)"
    c.execute(query)
    mydb.commit()

    query = "insert into Recipe_items(Recipe_id, Material_id, Quantity_required) values('Tea', 1, 1)"
    c.execute(query)
    mydb.commit()

    query = "insert into Recipe_items(Recipe_id, Material_id, Quantity_required) values('Tea', 2, 1)"
    c.execute(query)
    mydb.commit()

    query = "insert into Recipe_items(Recipe_id, Material_id, Quantity_required) values('Tea', 3, 1)"
    c.execute(query)
    mydb.commit()

    query = (
        "insert into Seller_info(Seller_id, name, contact, email) values(12345678, 'ABC', 1234567890, 'abc@gmail.com')"
    )
    c.execute(query)
    mydb.commit()
