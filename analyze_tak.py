#!/bin/env python
# coding=utf-8
import mysql.connector
from mysql.connector import Error
import csv
import sys
import argparse
from datetime import datetime
from BsJson import BsJson, BsJsonSection # Library to generate Beställningsstöd JSON

##################################################################################################
def printerr(text: str):
    """Print text to std error"""

    print(text, file=sys.stderr)

##################################################################################################
def show_table_info(conn, f, table_name, description, *where_clause):
    """Convenience frontend to show_db_info()"""

    sql_stmt = "SELECT COUNT(*) FROM " + table_name

    if where_clause:
        sql_stmt = sql_stmt + "WHERE " + where_clause

    show_db_info(conn, f, sql_stmt, description)


##################################################################################################
def show_db_info(conn, f, sql: str, description: str):
    """Function to do count(*) in the db and print it out on screen and in output file"""

    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()[0]
    f.write(f"{description}; {result}\n")
    print(f"{description}: {result}")


##################################################################################################
def create_summary_file():
    """Creates the summary information and writes it to screen and to a summary CSV-file"""

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

    summary_file = f"summary.{TP_NAME}.csv"
    f = open(summary_file, 'w', newline='', encoding='utf-8')
    f.write(f"TAK-information genererad {now}\n")
    f.close()
    f = open(summary_file, 'a', newline='', encoding='utf-8')

    print(f"\nDenna TAK innehåller:\n")
    f.write(f"\nDenna TAK innehåller:\n\n")

    show_table_info(takdb_connection, f, "Tjanstekomponent", "Antal tjänstekomponenter")
    show_table_info(takdb_connection, f, "Tjanstekontrakt", "Antal tjänstekontrakt")
    show_table_info(takdb_connection, f, "LogiskAdress", "Antal logiska adresser")
    show_table_info(takdb_connection, f, "Anropsbehorighet", "Antal anropsbehörigheter")
    show_table_info(takdb_connection, f, "Vagval", "Antal vägval")
    show_table_info(takdb_connection, f, "AnropsAdress", "Antal URL-er")

    print(f"\nFöljande märkligheter har identifierats i denna TAK (städning skall ske i samma ordning som listas nedan):\n")
    f.write(f"\nFöljande märkligheter har identifierats i denna TAK (städning skall ske i samma ordning som listas nedan):\n\n")

    for test_case in TestCase.test_cases:
        test_case.summary_report(takdb_connection, f)

    f.close()
    printerr(f"\nInformationen ovan har skrivits ut till {summary_file}")


##################################################################################################
class TestCase:
    """
    Class which defines TAK test cases.

    Each test case will exist as a separate instance. They will be stored and access through the static class list test_cases[].
    ...
    Attributes
    ----------
    id : str
        A string which identifies the test case. Will also be used to name the result files.
    description : str
        A description of the test case. Will be used on summary page and as heading in the result files.
    select_stmt : str
        The SQL Select statement the test case use to identify the problems.
    """

    test_cases = []

    def __init__(self, id, description, select_stmt):
        """Constructor which stores the instance in test_cases[]"""
        self.description = description
        self.id = id
        self.select_stmt = select_stmt
        TestCase.test_cases.append(self)

    def count_stmt(self):
        """Count the number of test results (number of problems)"""

        ix = self.select_stmt.index("FROM") - 1
        tail = self.select_stmt[ix:]
        return "SELECT COUNT(*)" + tail

    def generate_csv(self, conn):
        """ Create csv file with test results """

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

        cursor = conn.cursor()
        cursor.execute(self.select_stmt)
        result = cursor.fetchall()
        headings = [i[0] for i in cursor.description]

        filename = f"{self.id}.{TP_NAME}.csv"
        printerr(f"Generating {filename}")

        with open(filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([self.description])
            writer.writerow([f'Genererad, {now}'])
            writer.writerow(headings)
            writer.writerows(result)

    def generate_json(self, conn, tpname):
        """Create JSON file to correct the problems found.

         These files will be generated for a subset of the tests.
         The different columns from the SELECT results are mapped to different attributes in the JSON
         The BsJson class(es) are used to create the JSON files (defined in a separate source file).
         """
        if self.id == "url_not_used_in_routing" \
                or self.id == "authorization_based_on_SE"\
                or self.id == "url_based_on_ip_address"\
                or self.id == "routing_based_on_SE":
            return

        exclude_section = BsJsonSection()

        # Run the SELECT statement
        cursor = conn.cursor()
        cursor.execute(self.select_stmt)
        result = cursor.fetchall()

        # Go through all rows in answer from SELECT statement
        for record in result:

            if self.id == "tk_not_part_of_routing" or self.id == "tk_not_part_of_authorization":
                BsJsonSection.add_contract(exclude_section, record[1])
            elif self.id == "la_not_part_of_routing":
                BsJsonSection.add_logicalAddress(exclude_section,
                                                 record[1],
                                                 record[2]
                                                 )
            elif self.id == "components_not_used":
                BsJsonSection.add_component(exclude_section,
                                            record[1],
                                            record[2])
            elif self.id == "authorization_without_a_matching_routing":
                BsJsonSection.add_authorization(exclude_section,
                                                record[1],
                                                record[3],
                                                record[5]
                                                )
            elif self.id == "routing_without_a_matching_authorization":
                BsJsonSection.add_routing(exclude_section,
                                          record[4],
                                          None,
                                          record[1],
                                          record[3]
                                          )
            else:
                printerr(f"\nERROR: Unknown id in Testcase.generate_json: {self.id}")
                exit(1)

        content = BsJson(tpname)
        content.add_section("exclude", exclude_section)
        filename = f"{self.id}.{tpname}.json"
        content.print_json(filename)

    def summary_report(self, conn, f):
        """ Create a string specifying number of errors """

        cursor = conn.cursor()
        cursor.execute(self.count_stmt())
        result = cursor.fetchone()[0]
        f.write(f"{self.description}; {result}\n")
        printerr(f"{self.description}: {result}")


def define_test_cases():
    """The test cases (instances of the TestCase class) are created by this function"""

    TestCase(
        "authorization_without_a_matching_routing",
        "Anropsbehörigheter till icke existerande vägval",
        """
    SELECT DISTINCT    
        ab.id AS 'Anropsbehorighet ID',
        comp.hsaId AS 'Tjänstekonsument HSA-id',
        comp.beskrivning AS 'Tjänstekonsument beskrivning',
        la.hsaId AS 'Logisk adress',
        la.beskrivning AS 'Logisk adress beskrivning',
        tk.namnrymd AS 'Tjänstekontrakt namnrymd'
    FROM
        Anropsbehorighet ab,
        LogiskAdress la,
        Tjanstekomponent comp,
        Tjanstekontrakt tk
    WHERE
      ab.deleted IS NOT NULL
      AND ab.tomTidpunkt > CURDATE()
      AND ab.logiskAdress_id = la.id
      AND la.hsaId <> '*'
      AND la.hsaId <> 'SE'
      AND ab.tjanstekonsument_id = comp.id
      AND ab.tjanstekontrakt_id = tk.id
      AND tk.id NOT IN (
            SELECT DISTINCT vv.tjanstekontrakt_id
            FROM Vagval vv,
                LogiskAdress la2 -- LEO 2023-01-23
            WHERE
                vv.deleted IS NOT NULL
                AND vv.tomTidpunkt > CURDATE()
                AND vv.logiskAdress_id = la2.id -- LEO 2023-01-23
                AND (
                    vv.logiskAdress_id = ab.logiskAdress_id
                    OR la2.hsaId =  '*' -- LEO 2023-01-23
                    OR la2.hsaId = 'SE' -- LEO 2023-01-23 
                )
            )
    ORDER BY ab.id
        """)

    # ---------------------------------------------------------------------------------------------------
    TestCase(
        "routing_without_a_matching_authorization",
        "Vägval som saknar anropsbehörigheter",
        """
    SELECT DISTINCT vv.id            AS 'Vagval ID',
                la.hsaId         AS 'Logisk adress',
                la.beskrivning   AS 'Logisk adress beskrivning',
                tk.namnrymd      AS 'Tjänstekontrakt namnrymd',
                comp.hsaId       AS 'Tjänsteproducentens HSA-id',
                comp.beskrivning AS 'Tjänsteproducentens beskrivning'
    FROM Vagval vv,
         LogiskAdress la,
         Tjanstekomponent comp,
         Tjanstekontrakt tk,
         AnropsAdress aa
    WHERE vv.deleted IS NOT NULL
      AND vv.tomTidpunkt > CURDATE()  
      AND vv.logiskAdress_id = la.id
      AND vv.anropsAdress_id = aa.id
      AND aa.tjanstekomponent_id = comp.id
      AND vv.tjanstekontrakt_id = tk.id
      AND vv.tjanstekontrakt_id NOT IN (SELECT DISTINCT ab.tjanstekontrakt_id
                                        FROM Anropsbehorighet ab,
                                             LogiskAdress la2
                                        WHERE ab.deleted IS NOT NULL
                                          AND ab.tomTidpunkt > CURDATE()  
                                          AND ab.tjanstekontrakt_id = vv.tjanstekontrakt_id
                                          AND ab.logiskAdress_id = la2.id
                                          AND (
                                                    ab.logiskAdress_id = vv.logiskAdress_id
                                                OR la2.hsaId =  '*'
                                                OR la2.hsaId = 'SE'))
    ORDER BY vv.id    
        """)

    # ---------------------------------------------------------------------------------------------------
    TestCase(
        "la_not_part_of_routing",
        "Logiska adresser som inte förekommer i något vägval",
        """
    SELECT DISTINCT 
        la.id AS 'LogiskAdress ID',
        la.hsaId AS 'Logisk adress',
        la.beskrivning AS 'Beskrivning'
    FROM
        LogiskAdress la
    WHERE
        la.deleted IS NOT NULL
        AND la.hsaId <> '*'
        AND la.hsaId <> 'SE'
        AND la.id NOT IN (
            SELECT
               vv.logiskAdress_id
            FROM
               Vagval vv
            WHERE
                vv.deleted IS NOT NULL
                AND vv.tomTidpunkt > CURDATE()
            )
        """)

    # ---------------------------------------------------------------------------------------------------
    TestCase(
        "tk_not_part_of_authorization",
        "Tjänstekontrakt som inte förekommer i någon anropsbehörighet",
        """
        SELECT
            tk.id AS 'Tjanstekontrakt ID',
            tk.namnrymd AS 'Namnrymd'
        FROM
            Tjanstekontrakt tk
        WHERE
            tk.deleted IS NOT NULL
            AND tk.id NOT IN (
                SELECT
                   ab.tjanstekontrakt_id
                FROM
                   Anropsbehorighet ab
                WHERE
                    ab.deleted IS NOT NULL 
                    AND ab.tomTidpunkt > CURDATE()
                )
        """)

    # ---------------------------------------------------------------------------------------------------
    TestCase(
        "tk_not_part_of_routing",
        "Tjänstekontrakt som inte förekommer i något vägval",
        """
    
    SELECT DISTINCT
        tk.id AS 'Tjanstekontrakt ID',
        tk.namnrymd AS 'Namnrymd'
    FROM
        Tjanstekontrakt tk
    WHERE
        tk.deleted IS NOT NULL
        AND tk.id NOT IN (
            SELECT
               vv.tjanstekontrakt_id
            FROM
               Vagval vv
            WHERE
                vv.deleted IS NOT NULL 
                AND vv.tomTidpunkt > CURDATE()
            )
    """)
    # ---------------------------------------------------------------------------------------------------
    TestCase(
        "components_not_used",
        "Tjänstekomponenter som inte förekommer i något vägval eller någon anropsbehörighet",
        """
    SELECT DISTINCT
        comp.id AS 'Tjanstekomponent ID',
        comp.hsaId AS 'HSA-id',
        comp.beskrivning AS 'Beskrivning'
    FROM
        Tjanstekomponent comp
    WHERE
        comp.deleted IS NOT NULL
        AND comp.id NOT IN (
            SELECT
               ad.tjanstekomponent_id
            FROM
                Vagval vv,
                AnropsAdress ad
            WHERE
                ad.id = vv.anropsAdress_id
                AND vv.deleted IS NOT NULL
                AND vv.tomTidpunkt > CURDATE()
                AND ad.deleted IS NOT NULL
            )
        AND comp.id NOT IN (
            SELECT
                ab.tjanstekonsument_id
            FROM
                Anropsbehorighet ab
            WHERE
                ab.deleted IS NOT NULL
                AND ab.tomTidpunkt > CURDATE()
        )
        """)

    # ---------------------------------------------------------------------------------------------------

    TestCase(
        "authorization_based_on_SE",
        'Behörigheter baserade på logisk adress "SE" (bör ändras till "*")',
        """
        SELECT DISTINCT ab.id AS 'Anropsbehorighet ID',
        la.hsaId AS 'Logisk adress',
        tk.namnrymd AS 'Tjänstekontrakt',
        comp.hsaId AS 'Tjänstekonsument HSA-ID',
        comp.beskrivning AS 'Tjänstekońsument beskrivning'
        FROM Anropsbehorighet ab,
         LogiskAdress la,
         Tjanstekontrakt tk,
         Tjanstekomponent comp
        WHERE ab.deleted IS NOT NULL
          AND ab.tomTidpunkt > CURDATE()  
          AND ab.logiskAdress_id = la.id
          AND ab.tjanstekontrakt_id = tk.id
          AND ab.tjanstekonsument_id = comp.id
          AND la.hsaId = 'SE'
              """)

# ---------------------------------------------------------------------------------------------------
    TestCase(
        "routing_based_on_SE",
        'Vägval baserade på logisk adress "SE" (bör ändras till "*")',
        """
        SELECT DISTINCT vv.id AS 'Vagval ID',
            la.hsaId AS 'Logisk adress',
            tk.namnrymd AS 'Tjänstekontrakt',
            comp.hsaId AS 'Tjänsteproducent HSA-ID',
            comp.beskrivning AS 'Tjänsteproducent beskrivning'
            FROM Vagval vv,
             LogiskAdress la,
             Tjanstekontrakt tk,
             Tjanstekomponent comp,
             AnropsAdress aa
        WHERE vv.deleted IS NOT NULL
          AND vv.tomTidpunkt > CURDATE()
          AND vv.logiskAdress_id = la.id
          AND vv.tjanstekontrakt_id = tk.id
          AND vv.anropsAdress_id = aa.id
          AND aa.tjanstekomponent_id = comp.id
          AND la.hsaId = 'SE'

              """)

# ---------------------------------------------------------------------------------------------------
    TestCase(
        "url_not_used_in_routing",
        "URL-er som inte används i något vägval",
        """
        SELECT DISTINCT
            aa.id AS 'Anropsadress ID',
            aa.adress AS 'URL',
            tk.hsaId AS 'Tjänsteproducent HSA-id'
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
                    AND vv.tomTidpunkt > CURDATE()
            )
        ORDER BY aa.adress
           """)

    # ---------------------------------------------------------------------------------------------------
    TestCase(
        "url_based_on_ip_address",
        "URL-er som specificerar IP-adresser istället för DNS-namn",
        """
        SELECT DISTINCT
            aa.id AS 'Anropsadress ID',
            aa.adress AS 'URL',
            comp.hsaId AS 'Tjänsteproducent HSA-id'
        FROM
            AnropsAdress aa,
            Tjanstekomponent comp
        WHERE
            aa.deleted IS NOT NULL
            AND aa.tjanstekomponent_id = comp.id
            AND aa.adress REGEXP 'https?:\/\/(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
           """)


##################################################################################################
#                                 Main Program
##################################################################################################
# Script argument defaults
host_default = "localhost"
user_default = "dbuser"
password_default = "dbuser"
database_default = "takv_prod_20230112"

# ------------------------------------------------------------------------------------------
# Set up the argument parsing
parser = argparse.ArgumentParser()

parser.add_argument("-c", "--csv", action="store_true", help="Generate csv files")
parser.add_argument("-i", "--information", action="store_true", help="Generate information summary file")
parser.add_argument("-j", "--json", action="store_true", help="Generate json files")
parser.add_argument("-t", "--tpname", action="store", help='TP name, must end with "_PROD", "_QA" or "_TEST',
                    required=True)
parser.add_argument("-s", "--server", action="store", help="Name of DB host", default=host_default)
parser.add_argument("-u", "--db_user", action="store", help="Name of DB user", default=user_default)
parser.add_argument("-p", "--db_password", action="store", help="DB user password", default=password_default)
parser.add_argument("-d", "--db_name", action="store", help="DB name", default=database_default)

args = parser.parse_args()

TP_NAME = args.tpname.upper()

if not (TP_NAME.endswith("_PROD") or TP_NAME.endswith("_QA") or TP_NAME.endswith("_TEST")):
    printerr('tpname name must end with "_PROD", "_QA" or "_TEST')
    exit(1)

if not (args.csv or args.json or args.information):
    printerr("At least one of (-c | -j | -i) must be specified")
    parser.print_help()
    exit(1)

# ------------------------------------------------------------------------------------------
# Connect to the TAK database
try:
    takdb_connection = mysql.connector.connect(
        host=args.server,
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

# ------------------------------------------------------------------------------------------
# Create the test cases
define_test_cases()

# ------------------------------------------------------------------------------------------
# Do the work based on user specified flags
if (args.information):
    create_summary_file()

if (args.csv):
    for test_case in TestCase.test_cases:
        test_case.generate_csv(takdb_connection)

if (args.json):
    for test_case in TestCase.test_cases:
        test_case.generate_json(takdb_connection, TP_NAME)

# ------------------------------------------------------------------------------------------
# Close and exit
takdb_connection.close()
exit(0)
