import json
import os
import sys
import logging
import pymysql
from datetime import datetime
import uuid
from base64 import b64decode
import boto3
from dateutil.parser import parse

# rds settings
db_host  = os.environ["db_host"]
name = os.environ['db_username1']
password = os.environ['db_password1']
# ENCRYPTED_name = os.environ['db_username']
# ENCRYPTED_password = os.environ['db_password']

# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container

# print("1")
# name = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_name))['Plaintext'].decode('utf-8')
# password = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_password))['Plaintext'].decode('utf-8')
# print("2")

db_name = "parkingLot"

price_per_15 = 3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    print("before connn")
    conn = pymysql.connect(host=db_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def lambda_handler(event, context):
    
    if event['path'] == "retry":
    
        plate = event['queryStringParameters']['plate']
        parking_lot = event['queryStringParameters']['parkingLot']
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with conn.cursor() as cursor:
            cursor.execute("create table payment ( ticketID varchar(255) NOT NULL, plate varchar(255) NOT NULL, parkingLot int NOT ,entryTime DATE, PRIMARY KEY (ticketID))")
            id = str(uuid.uuid1())
            print("before sql insert")
            sql = f"INSERT INTO `payment` (`id`, `plate`, `parkingLot`, `entryTime`) VALUES ({id}, {plate}, {parking_lot}, {time})"
            try: 
                cursor.execute(sql)
                conn.commit()
            except (pymysql.Error, pymysql.Warning) as e:
                print("cannot insert")
                return {
                    'statusCode': 400,
                    'body': json.dumps(e)
                }
        conn.commit()
        print("insert")
        print(id)
        return {
            'statusCode': 200,
            'body': json.dumps('Hello, your ticket id is ' + id)
        }
    
    if event["path"] == 'exit':
        ticketId = event['queryStringParameters']['ticketId']
        with conn.cursor() as cursor:
            try: 
                sql = f"SELECT * FROM payment WHERE ID = {ticketId}"
                cursor.execute(sql)
            except (pymysql.Error, pymysql.Warning) as e:
                 return {
                    'statusCode': 400,
                    'body': json.dumps(e)
                }
            data = cursor.fetchone()
            now_time = datetime.now()
            start_time = data["entryTime"]
            plate = data["plate"]
            parking_lot = data["parkingLot"]
            
            delta = now_time - parse(start_time)
            minutes_passed = delta.seconds // 60
            
            added = 0
            if (minutes_passed % 15 != 0):
                added = 1
            payment = minutes_passed / 15 +  added
            
            total_price = payment * price_per_15
            
            return_string =f"goodbye {plate} , {parking_lot} Thank you for parking, your total acount is {total_price}."
            
            print(return_string)
            return {
            'statusCode': 200,
            'body': json.dumps(return_string)
            }