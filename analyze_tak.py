# coding=utf-8
import mysql.connector
from mysql.connector import Error
import csv
import sys
import argparse
from datetime import datetime


##################################################################################################
def printerr(text):
    print(text, file=sys.stderr)


##################################################################################################
def show_db_info(conn, f, table_name, description):
    sql_stmt = "SELECT COUNT(*) FROM " + table_name

    cursor = conn.cursor()
    cursor.execute(sql_stmt)
    result = cursor.fetchone()[0]
    f.write(f"{description}: {result}\n")
    print(f"{description}: {result}")


##################################################################################################
#                                 Main Program
##################################################################################################
# Defaults
host_default = "localhost"
user_default = "TPDB"
password_default = "TPDB"
database_default = "TAK20200327"

parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", "--csv", action="store_true", help="Generate csv files")
group.add_argument("-j", "--json", action="store_true", help="Generate json files")
parser.add_argument("-s", "--db_server", action="store", help="Name of DB host", default=host_default)
parser.add_argument("-u", "--db_user", action="store", help="Name of DB user", default=user_default)
parser.add_argument("-p", "--db_password", action="store", help="DB user password", default=password_default)
parser.add_argument("-d", "--db_name", action="store", help="DB name", default=database_default)

args = parser.parse_args()

"""
if (environment not in ARG_ENVIRONMENT or target not in ARG_TARGET or phase not in ARG_PHASE):
    parser.print_help()
    exit()
"""

try:
    takdb_connection = mysql.connector.connect(
        host=args.db_server,
        user=args.db_user,
        password=args.db_password,
        database=args.db_name
    )
    if takdb_connection.is_connected():
        printerr(f'Connected to {args.db_name}')

except Error as e:
        printerr(f'Error connecting to {args.db_name}')
        parser.print_help()
        exit(1)


##################################################################################################
JUST_NOW: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

test_cases = []

class TestCase:
    def __init__(self, id, description, headings, select_stmt):
        self.description = description
        self.id = id
        self.headings = headings
        self.select_stmt = select_stmt
        test_cases.append(self)

    def count_stmt(self):
        ix = self.select_stmt.index("FROM") - 1
        tail = self.select_stmt[ix:]
        return "SELECT COUNT(*)" + tail

    def generate_csv(self, conn):
        """ Create csv file with test results """
        cursor = conn.cursor()
        cursor.execute(self.select_stmt)
        result = cursor.fetchall()

        filename = self.id + ".csv"
        printerr(f"Generating {filename}")

        with open(filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([self.description])
            writer.writerow([f'Genererad, {JUST_NOW}'])
            writer.writerow(self.headings)
            writer.writerows(result)

    def summary_report(self, conn, f):
        """ Return string specifying number of errors """
        cursor = conn.cursor()
        cursor.execute(self.count_stmt())
        result = cursor.fetchone()[0]
        f.write(f"{self.description}: {result}\n")
        print(f"{self.description}: {result}")

# =================================================================================================

TestCase(
        "la_not_part_of_routing",
        "Logiska adresser som inte förekommer i något vägval",
        ["Id", "Logisk adress", "Beskrivning"],
        """
SELECT DISTINCT 
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
    """)



# -----------------------------------------------------------------------------------------
TestCase(
    "authorization_without_a_matching_routing",
    "Anropsbehörigheter till icke existerande vägval.",
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
      vv.deleted IS NOT NULL
        AND vv.tjanstekontrakt_id = ab.tjanstekontrakt_id
        AND vv.logiskAdress_id = ab.logiskAdress_id
    )
ORDER BY ab.id
    """)


    # ---------------------------------------------------------------------------------------------------
TestCase(
    "tk_not_part_of_routing",
    "Tjänstekontrakt som inte förekommer i något vägval",
    ["Id", "Tjänstekontraktets namnrymd"],
    """

SELECT DISTINCT
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
""")

    # ---------------------------------------------------------------------------------------------------
TestCase(
    "tk_not_part_of_authorization",
    "Tjänstekontrakt som inte förekommer i någon anropsbehörighet",
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
    """)

    # ---------------------------------------------------------------------------------------------------
TestCase(
    "components_not_used",
    "Tjänstekomponenter som inte förekommer i något vägval eller någon anropsbehörighet",
    ["Id", "Tjänstekomponentens HSA-id", "Tjänstekomponentens beskrivning"],
    """
SELECT DISTINCT
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
    """)

    # ---------------------------------------------------------------------------------------------------
TestCase(
    "url_not_used_in_routing",
    "URL-er som inte används i något vägval",
    ["Id", "URL", "Tjänsteproducent"],
    """
SELECT DISTINCT
    aa.id,
    aa.adress,
    tk.hsaId
FROM
    AnropsAdress aa,
    Tjanstekomponent tk
WHERE
    aa.deleted IS NOT NULL
    AND tk.deleted IS NOT NULL
    AND aa.tjanstekomponent_id = tk.id
    AND aa.id NOT IN (
        SELECT
           vv.anropsAdress_id
        FROM Vagval vv
        WHERE
            vv.deleted IS NOT NULL
    )
ORDER BY aa.adress
   """)


summary_file = "summary.csv"
f = open(summary_file, 'w', newline='', encoding='utf-8')
f.write(f"TAK-information genererad {JUST_NOW}\n")
f.close
f = open(summary_file, 'a', newline='', encoding='utf-8')

show_db_info(takdb_connection, f, "Tjanstekomponent", "Antal tjänstekomponenter")
show_db_info(takdb_connection, f, "Tjanstekontrakt", "Antal tjänstekontrakt")
show_db_info(takdb_connection, f, "LogiskAdress", "Antal logiska adresser")
show_db_info(takdb_connection, f, "Vagval", "Antal vägval")
show_db_info(takdb_connection, f, "Anropsbehorighet", "Antal anropsbehörigheter")
show_db_info(takdb_connection, f, "AnropsAdress", "Antal URL-er")

for item in test_cases:
    item.summary_report(takdb_connection, f)

f.close
printerr(f"Summary information above is written to {summary_file}")

if args.csv:
    for item in test_cases:
        item.generate_csv(takdb_connection)

takdb_connection.close()
