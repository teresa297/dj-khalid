import mysql.connector as mysql

conn=mysql.connect(host="localhost",user="root",password="mysql",database="jr")


cursor=conn.cursor()

def insert_user(name, username, user_type, password):
    sql = """
    INSERT INTO User (Name, Username, UserType, Password) 
    VALUES (%s, %s, %s, %s)
    """
    values = (name, username, user_type, password)

    try:
        cursor.execute(sql, values)
        conn.commit()
        print("User inserted successfully!")
    except mysql.connector.Error as err:
        print("Error:", err)



