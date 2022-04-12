import mysql.connector
import csv
from datetime import datetime


##################################################################################################
def printerr(text):
    print(text, file=sys.stderr)


##################################################################################################
def perform_test(
        conn,
        description,
        filename,
        header,
        sql
):
    """ Create csv file with test results """

    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # for x in result:
    #   print(x)

    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([description])
        writer.writerow([f'Genererad, {NOW}'])
        writer.writerow(header)
        writer.writerows(result)


##################################################################################################

NOW: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

test_definitions = [

    [
        "Logiska adresser som inte förekommer i något vägval",
        "la_not_part_of_routing.csv",
        ["Id", "Logisk adress", "Beskrivning"],
        """
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
    ],

    [
        "Logiska adresser som inte förekommer i någon behörighet. Observera att det kan förekomma vid användning av standardbehörighet.",
        "la_not_part_of_authorization.csv",
        ["Id", "Logisk adress", "Beskrivning"],
        """
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
           ab.logiskAdress_id
        FROM
           Anropsbehorighet ab
        WHERE
            ab.deleted = 0
        )
    """
    ],

    [
        "Anropsbehörigheter till icke existerande vägval.",
        "autorization_without_a_matching_routing.csv",
        ["Tjänstekonsument HSA-id", "Tjänstekonsument beskrivning", "Tjänstekontrakt", "Logisk adress", "Logisk adress beskrivning"],
        """
SELECT DISTINCT
    comp.hsaId AS 'Tjänstekonsument HSA-id',
    comp.beskrivning AS 'Tjänstekonsument beskrivning',
    tk.namnrymd AS 'Tjänstekontrakt',
    la.hsaId AS 'Logisk adress',
    la.beskrivning AS 'Logisk adress beskrivning'
FROM
    Anropsbehorighet ab,
    LogiskAdress la,
    Tjanstekomponent comp,
    Tjanstekontrakt tk
WHERE
  ab.deleted IS NOT NULL
  AND ab.logiskAdress_id = la.id
  AND ab.tjanstekonsument_id = comp.id
  AND ab.tjanstekontrakt_id = tk.id
  AND la.id NOT IN (
      SELECT vv.logiskAdress_id
      FROM Vagval vv
      WHERE
        vv.tjanstekontrakt_id = ab.tjanstekontrakt_id
        AND vv.logiskAdress_id = ab.logiskAdress_id
    )
ORDER BY ab.id
    """

    ]
]

takdb_connection = mysql.connector.connect(
    host="localhost",
    user="TPDB",
    password="TPDB",
    database="RTP_PROD"
)

for test in test_definitions:
    perform_test(takdb_connection, test[0], test[1], test[2], test[3] )

takdb_connection.close()
