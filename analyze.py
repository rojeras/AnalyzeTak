import mysql.connector
import csv
from datetime import datetime


##################################################################################################
def printerr(text):
    print(text, file=sys.stderr)


##################################################################################################
def la_not_part_of_routing(conn):
    """ List logical addresses not par of a routing"""

    sql: str = """
SELECT
    la.id,
    la.hsaId,
    la.beskrivning
FROM
    LogiskAdress la
WHERE
    la.deleted = 0
    AND la.id NOT IN (
        SELECT
           vv.logiskAdress_id
        FROM
           Vagval vv
        WHERE
            vv.deleted = 0
        )
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # for x in result:
    #   print(x)

    with open('la_not_part_of_routing.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Logiska adresser som inte förekommer i något vägval"])
        writer.writerow([f'Genererad, {NOW}'])
        writer.writerow(["Id", "Logisk adress", "Beskrivning"])
        writer.writerows(result)


##################################################################################################

NOW: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

takdb_connection = mysql.connector.connect(
    host="localhost",
    user="TPDB",
    password="TPDB",
    database="RTP_PROD"
)

la_not_part_of_routing(takdb_connection)

takdb_connection.close()
