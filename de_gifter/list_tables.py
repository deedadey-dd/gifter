# import os
# import sqlite3
#
# # Connect to your SQLite database
# conn = sqlite3.connect('db.sqlite3')
# cursor = conn.cursor()
#
# # Execute a query to list tables
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()
#
# # Print the tables
# print("Tables in the database:")
# for table in tables:
#     print(table[0])
#
# # Close the connection
# conn.close()


# import requests
#
#
# endPoint = os.environ['SMS_ENDPOINT']
# apiKey = os.environ['SMS_API']
# phone_pin = '23445'
# data = {
#   'recipient[]': ['233205448044'],
#   'sender': 'Dee Code',
#   'message': f'Enter the following PIN to confirm your phone number\n {phone_pin} third msg',
# }
# url = endPoint + '?key=' + apiKey
# # print(url)
# response = requests.post(url, data)
# # print(response.status_code)
# # data = response.json()
# # print(data)

import random
import string

phone_confirmation_pin = ''.join(random.choices(string.digits, k=6))

print(type(phone_confirmation_pin))

