import mysql.connector
from mysql.connector import Error


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="gloria2005",
            database="HELLOWORLD",
            charset="utf8"
        )

        if connection.is_connected():
            return connection

        return None

    except Error as error:
        print("Database connection error:", error)
        return None


# ==========================================================
# CREATE TABLES
# ==========================================================

def create_tables():

    connection = create_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        # USERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role ENUM('student', 'admin')
                    NOT NULL DEFAULT 'student'
            )
        """)

        # WORKERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                worker_id INT AUTO_INCREMENT PRIMARY KEY,
                staff_no VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                department VARCHAR(100),
                role ENUM(
                    'lecturer',
                    'admin',
                    'support'
                ) DEFAULT 'lecturer',
                status ENUM(
                    'active',
                    'inactive'
                ) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # COURSES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(20) UNIQUE NOT NULL,
                course_name VARCHAR(100) NOT NULL,
                credits INT DEFAULT 3
            )
        """)

        # WORKER CREDENTIALS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_credentials (
                worker_id INT PRIMARY KEY,
                password_hash VARCHAR(255) NOT NULL,

                CONSTRAINT fk_worker_credentials_worker
                FOREIGN KEY (worker_id)
                REFERENCES workers(worker_id)
                ON DELETE CASCADE
            )
        """)

        connection.commit()

        print("All tables are ready.")
        return True

    except Error as error:

        connection.rollback()
        print("Table creation error:", error)
        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================================
# INSERT USER
# ==========================================================

def insert_user(name, email, password, role="student"):

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM users
            WHERE email = %s
        """, (email,))

        if cursor.fetchone():

            return False, "An account with this email already exists."

        cursor.execute("""
            INSERT INTO users
            (name, email, password, role)
            VALUES (%s, %s, %s, %s)
        """, (
            name,
            email,
            password,
            role
        ))

        connection.commit()

        return True, "Account created successfully."

    except Error as error:

        connection.rollback()
        print("Insert user error:", error)

        return False, "Unable to create account."

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================================
# FIND USER
# ==========================================================

def get_user_by_email(email):

    connection = create_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                password,
                role
            FROM users
            WHERE email = %s
        """, (email,))

        return cursor.fetchone()

    except Error as error:

        print("Find user error:", error)
        return None

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================================
# GET ALL USERS
# ==========================================================

def get_users():

    connection = create_connection()

    if connection is None:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role
            FROM users
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    except Error as error:

        print("Get users error:", error)
        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================================
# GET WORKERS
# ==========================================================

def get_workers():

    connection = create_connection()

    if connection is None:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                worker_id,
                staff_no,
                name,
                email,
                department,
                role,
                status,
                created_at
            FROM workers
            ORDER BY created_at DESC
        """)

        return cursor.fetchall()

    except Error as error:

        print("Get workers error:", error)
        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ==========================================================
# GET COURSES
# ==========================================================

def get_courses():

    connection = create_connection()

    if connection is None:
        return []

    cursor = None

    try:
 
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                course_id,
                code,
                course_name,
                credits
            FROM courses
            ORDER BY course_name
        """)

        return cursor.fetchall()

    except Error as error:

        print("Get courses error:", error)
        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()