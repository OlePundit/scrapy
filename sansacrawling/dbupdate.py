import csv
import os
import mysql.connector  # Use MySQL connector instead of psycopg2

# Database connection setup
conn = mysql.connector.connect(
    host="localhost",
    user="salvacar_admin",
    password="Glennisgood14$",
    database="salvacar_self"
)
cursor = conn.cursor()

# Path to the CSV file
csv_file_path = 'output.csv'

# Open the CSV file and read its contents
with open(csv_file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Extract the user-related data
        email = row.get("email")
        user_data = {
            "name": row.get("name"),
            "user_type": row.get("user_type"),
            "email": email,
            "image": row.get("image"),
            "password": row.get("password"),
        }

        # Check if email already exists in the users table
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # If the email already exists, skip this row or update user if necessary
            print(f"User with email {email} already exists. Skipping...")
            user_id = existing_user[0]
        else:
            # If the email does not exist, insert the new user into the users table
            cursor.execute("""
                INSERT INTO users (name, user_type, email, image, password)
                VALUES (%s, %s, %s, %s, %s);
            """, (user_data['name'], user_data['user_type'], user_data['email'], user_data['image'], user_data['password']))
            user_id = cursor.lastrowid  # Get the new user_id

            print(f"Inserted new user with email {email}. User ID: {user_id}")

        # Extract the job-related data
        job_data = {
            "title": row.get("title"),
            "location": row.get("location"),
            "category": row.get("category"),
            "price": row.get("price"),
            "deadline": row.get("deadline"),
            "description": row.get("description"),
            "jobtype": row.get("jobtype"),
            "requirements": row.get("requirements"),
            "currency": row.get("currency"),
            "slug": row.get("slug"),
            "user_id": user_id  # Add the user_id for the job
        }

        # Insert the job into the jobs table and link to the user
        cursor.execute("""
            INSERT INTO jobs (title, location, category, price, deadline, description, jobtype, requirements, currency, slug, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            job_data['title'], job_data['location'], job_data['category'], job_data['price'], 
            job_data['deadline'], job_data['description'], job_data['jobtype'], job_data['requirements'], 
            job_data['currency'], job_data['slug'], job_data['user_id']
        ))

        print(f"Inserted job '{job_data['title']}' for user ID {user_id}")

    # Commit changes to the database and close the connection
    conn.commit()

# Delete the CSV file after processing
try:
    os.remove(csv_file_path)
    print(f"CSV file {csv_file_path} has been deleted.")
except Exception as e:
    print(f"Failed to delete CSV file: {e}")

# Close the database connection
cursor.close()
conn.close()
