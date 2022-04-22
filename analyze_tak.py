import mysql.connector
import csv
import sys
import argparse
from datetime import datetime


##################################################################################################
def printerr(text):
    print(text, file=sys.stderr)


##################################################################################################
def perform_test(
        conn,
        description: str,
        filename,  #: Union[str, List[str]],
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
#                                 Main Program
##################################################################################################
# Parse arguments
parser = argparse.ArgumentParser()

# analyze_tak.py [-c | --csv] [-j | --json] [-s | --statistics] [-h db_hostname] [-u db_user] [-p db_password] [-d db_dbname]
# Environment: prod | qa
# Target: ntjp | rtp
# Phase: update | remove | rollback

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", "--csv", action="store_true", help="Generate csv files")
group.add_argument("-j", "--json", action="store_true", help="Generate json files")
group.add_argument("-i", "--information", action="store_true", help="Show statistics information of the TAK")
parser.add_argument("-s", "--db_server", action="store", help="Name of DB host", default="localhost")
parser.add_argument("-u", "--db_user", action="store", help="Name of DB user", default="TPDB")
parser.add_argument("-p", "--db_password", action="store", help="DB user password", default="TPDB")
parser.add_argument("-d", "--db_name", action="store", help="DB name", default="RTP_PROD")

args = parser.parse_args()

# environment = args.environment.lower()
# target = args.target.lower()
# phase = args.phase.lower()
# create_sample = args.sample
# service_productions_file = args.filename[0]

exit()
"""
if (environment not in ARG_ENVIRONMENT or target not in ARG_TARGET or phase not in ARG_PHASE):
    parser.print_help()
    exit()
"""

takdb_connection = mysql.connector.connect(
    host="localhost",
    user="TPDB",
    password="TPDB",
    database="RTP_PROD"
)


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
    # ---------------------------------------------------------------------------------------------------
    # Removed since it might not be an error
#     [
#         "Logiska adresser som inte förekommer i någon behörighet. Observera att det kan förekomma vid användning av "
#         "standardbehörighet.",
#         "la_not_part_of_authorization.csv",
#         ["Id", "Logisk adress", "Beskrivning"],
#         """
# SELECT
#     la.id,
#     la.hsaId, # Addera TK
#     la.beskrivning
# FROM
#     LogiskAdress la
# WHERE
#     la.deleted = 0
#     AND la.id NOT IN (
#         SELECT
#            ab.logiskAdress_id
#         FROM
#            Anropsbehorighet ab
#         WHERE
#             ab.deleted = 0
#         )
#     """
#     ],

    # ---------------------------------------------------------------------------------------------------
    [
        "Anropsbehörigheter till icke existerande vägval.",
        "authorization_without_a_matching_routing.csv",
        ["Tjänstekonsument HSA-id", "Tjänstekonsument beskrivning", "Tjänstekontrakt", "Logisk adress",
         "Logisk adress beskrivning"],
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
      vv.deleted IS NOT NULL
        AND vv.tjanstekontrakt_id = ab.tjanstekontrakt_id
        AND vv.logiskAdress_id = ab.logiskAdress_id
    )
ORDER BY ab.id
    """

    ],


    # ---------------------------------------------------------------------------------------------------
    [
    "Tjänstekontrakt som inte förekommer i något vägval",
    "tk_not_part_of_routing.csv",
    ["Id", "Tjänstekontraktets namnrymd"],
    """

SELECT
    tk.id,
    tk.namnrymd
FROM
    Tjanstekontrakt tk
WHERE
    tk.deleted = 0
    AND tk.id NOT IN (
        SELECT
           vv.tjanstekontrakt_id
        FROM
           Vagval vv
        WHERE
            vv.deleted = 0
        )
"""
    ],


    # ---------------------------------------------------------------------------------------------------
    [
        "Tjänstekontrakt som inte förekommer i någon anropsbehörighet",
        "tk_not_part_of_authorization.csv",
        ["Id", "Tjänstekontraktets namnrymd"],
        """
    
    SELECT
        tk.id,
        tk.namnrymd
    FROM
        Tjanstekontrakt tk
    WHERE
        tk.deleted = 0
        AND tk.id NOT IN (
            SELECT
               ab.tjanstekontrakt_id
            FROM
               Anropsbehorighet ab
            WHERE
                ab.deleted = 0
            )
    """
    ],


    # ---------------------------------------------------------------------------------------------------
    [
        "Tjänstekomponenter som inte förekommer i något vägval eller någon anropsbehörighet",
        "components_not_used.csv",
        ["Id", "Tjänstekomponentens HSA-id", "Tjänstekomponentens beskrivning"],
        """
SELECT
    comp.id,
    comp.hsaId,
    comp.beskrivning
FROM
    Tjanstekomponent comp
WHERE
    comp.deleted = 0
    AND comp.id NOT IN (
        SELECT
           ad.tjanstekomponent_id
        FROM
            Vagval vv,
            AnropsAdress ad
        WHERE
            ad.id = vv.anropsAdress_id
            AND vv.deleted = 0
            AND ad.deleted = 0
        )
    AND comp.id NOT IN (
        SELECT
            ab.tjanstekonsument_id
        FROM
            Anropsbehorighet ab
        WHERE
            ab.deleted = 0
    )
    """
    ],


    # ---------------------------------------------------------------------------------------------------
    [
        "URL-er som inte används i något vägval",
        "url_not_used_in_routing.csv",
        ["Id", "URL"],
        """
SELECT DISTINCT
    aa.id,
    aa.adress
FROM
    AnropsAdress aa
WHERE
    aa.deleted IS NOT NULL
    AND aa.id NOT IN (
        SELECT
           vv.anropsAdress_id
        FROM Vagval vv
        WHERE
            vv.deleted IS NOT NULL
    )
ORDER BY aa.adress
   """
    ]

]



for test in test_definitions:
    perform_test(takdb_connection, test[0], test[1], test[2], test[3])

takdb_connection.close()
