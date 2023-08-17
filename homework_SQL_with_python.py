import psycopg2

def create_db(conn):
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clients (
                id SERIAL PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Phones (
                id SERIAL PRIMARY KEY,
                client_id INT REFERENCES Clients(id) ON DELETE CASCADE,
                phone_number TEXT
            )
        ''')
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO Clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id', (first_name, last_name, email))
        client_id = cursor.fetchone()[0]
        if phones:
            for phone in phones:
                cursor.execute('INSERT INTO Phones (client_id, phone_number) VALUES (%s, %s)', (client_id, phone))
        conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO Phones (client_id, phone_number) VALUES (%s, %s)', (client_id, phone))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cursor:
        if first_name:
            cursor.execute('UPDATE Clients SET first_name=%s WHERE id=%s', (first_name, client_id))
        if last_name:
            cursor.execute('UPDATE Clients SET last_name=%s WHERE id=%s', (last_name, client_id))
        if email:
            cursor.execute('UPDATE Clients SET email=%s WHERE id=%s', (email, client_id))
        if phones:
            cursor.execute('DELETE FROM Phones WHERE client_id=%s', (client_id,))
            for phone in phones:
                cursor.execute('INSERT INTO Phones (client_id, phone_number) VALUES (%s, %s)', (client_id, phone))
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM Phones WHERE client_id=%s AND phone_number=%s', (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM Phones WHERE client_id=%s', (client_id,))
        cursor.execute('DELETE FROM Clients WHERE id=%s', (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cursor:
        query = 'SELECT * FROM Clients WHERE '
        conditions = []
        params = []
        if first_name:
            conditions.append('first_name = %s')
            params.append(first_name)
        if last_name:
            conditions.append('last_name = %s')
            params.append(last_name)
        if email:
            conditions.append('email = %s')
            params.append(email)
        if phone:
            conditions.append('id IN (SELECT client_id FROM Phones WHERE phone_number = %s)')
            params.append(phone)
        query += ' AND '.join(conditions)
        cursor.execute(query, tuple(params))
        clients = cursor.fetchall()
        return clients

with psycopg2.connect(database="test_work", user="postgres", password="2467") as conn:
    create_db(conn)

    add_client(conn, "John", "Jostar", "john@jostar.com", ["7-123-456-7890", "7-987-654-3210"])
    add_client(conn, "Dio", "Brando", "dio@killjostar.com", ["6-666-666-6666"])
    add_phone(conn, 1, "8-800-555-3535")

    change_client(conn, 1, first_name="Jonathan", phones=["999-999-9999"])

    delete_phone(conn, 1, "7-123-456-7890")

    delete_client(conn, 1)

    found_clients = find_client(conn, first_name="Dio")
    print("Found Clients:")
    for client in found_clients:
        print(client)

conn.close()
