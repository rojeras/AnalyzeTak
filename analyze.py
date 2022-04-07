import mysql.connector

takdb = mysql.connector.connect(
    host="localhost",
    user="TPDB",
    password="TPDB",
    database="RTP_PROD"
)

cursor = takdb.cursor()

cursor.execute("SELECT * FROM AnropsAdress")

result = cursor.fetchall()

for x in result:
    print(x)