import sqlite3

## Connect to SQLite
connection = sqlite3.connect("student.db")

## Create a cursor object to create table and insert records
cursor = connection.cursor()

## Create the table
table_info="""
CREATE TABLE student(
    name VARCHAR(25),
    class VARCHAR(25),
    section VARCHAR(25),
    marks INT
)
"""

cursor.execute(table_info)

## Insert some more records
cursor.execute('''INSERT INTO student VALUES('Aayush', 'Data Science', 'A', 90)''')
cursor.execute('''INSERT INTO student VALUES('Maitree', 'Data Science', 'A', 100)''')
cursor.execute('''INSERT INTO student VALUES('Sundram', 'Data Science', 'B', 86)''')
cursor.execute('''INSERT INTO student VALUES('Avinash', 'Information Technology', 'A', 50)''')
cursor.execute('''INSERT INTO student VALUES('Tarush', 'Information Technology', 'A', 35)''')

## Display all the records
print("The inserted records are:")
data = cursor.execute('''SELECT * FROM student''')
for row in data:
    print(row)

## Commit your changes in the database
connection.commit()
connection.close()