import mysql.connector as mysql

# Establish connection
conn = mysql.connect(host="localhost", user="root", password="mysql", database="jr")
cursor = conn.cursor()

def insert_skill(skilln):
    sql = "INSERT INTO skill (Name) VALUES (%s)"
    values = (skilln,)

    try:
        cursor.execute(sql, values)
        conn.commit()
        print("Skill inserted successfully!")
    except mysql.Error as err:
        print("Error:", err)

# Infinite loop with exit condition
while True:
    skill = input("Enter skill (or type 'exit' to quit): ")
    if skill.lower() == 'exit':
        break
    insert_skill(skill)

# Close connection
cursor.close()
conn.close()
