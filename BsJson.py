from datetime import datetime
import json
import sys

# This file contains two classes to manage and generate the BS-json files

def printerr(text):
    print(text, file=sys.stderr)


class BsJson:
    """ A class to create BS JSON files

    It manages the JSON file header information and references the include and exclude sections. The Json information
    is managed as python dictionaries internally, and converted to JSON when printed.

    Attributes
    ----------
    plattform : str
        The name of the TP instance (example "RTP-PROD"). Mapped to "plattform" in the JSON file.
    excutor : str
        Name of the organization doing the TAK change, mapped to "utforare" in the JSON file.
    include : BsJsonSection
        An instance of BsJsonSection which contains the include section.
    exclude : BsJsonSection
        An instance of BsJsonSection which contains the exclude section.
    """

    def __init__(self, plattform, executor="Region Stockholm - Forvaltningsobjekt Informationsinfrastruktur"):
        """Constructor"""
        self.plattform = plattform
        self.executor = executor
        self.include = None
        self.exclude = None

    def add_section(self, type, section):
        """Method which receives and stores a BsJsonSection instance (include or exclude) """

        if type == "include":
            self.include = section
        elif type == "exclude":
            self.exclude = section
        else:
            printerr(f"add_section called with unknown type: {type}")
            exit(1)

    def get_header(self):
        """Method which creates the header info in the BS Json file """


        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

        return {
            "plattform": self.plattform,
            "formatVersion": "1.0",
            "version": "1",
            "bestallningsTidpunkt": now,
            "utforare": self.executor,
            "genomforandeTidpunkt": now,
        }

    def print_json(self, *file):
        """Method to collect all information and write the Json data to a file """
        content = self.get_header()
        if self.include:
            content["inkludera"] = BsJsonSection.get_json(self.include)
        if self.exclude:
            content["exkludera"] = BsJsonSection.get_json(self.exclude)

        if file:
            filename = file[0]
            printerr(f"Generating {filename}")
            f = open(filename, 'w', newline='', encoding='utf-8')
            f.write(json.dumps(content, ensure_ascii=False, indent=4))
            f.close()
        else:
            print(json.dumps(content, ensure_ascii=False, indent=4))


class BsJsonSection:
    """A class which represents a BS Json include or exclude section

    The different constituents of a section is added to an instance. It can then be retrieved in the form af a python
    dictionary.

    Attributes
    ----------
    logicalAddresses : list of dicts
        Store dicts representing LA
    components :  list of dicts
        Store dicts representing components
    contracts :  list of dicts
        Store dicts representing contracts
    routings :  list of dicts
        Store dicts representing routings (vagval)
    authorities :  list of dicts
        Store dicts representing authorities (behorighet)
    """


    def __init__(self):
        """Constructor"""

        self.logicalAddresses = []
        self.components = []
        self.contracts = []
        self.routings = []
        self.authorities = []

    def add_logicalAddress(self,
                           id,
                           *description):
        """Add a unique dict representing TAK-info to instance."""

        logicalAddress = {
            "hsaId": id
        }

        if description:
            logicalAddress["beskrivning"] = description[0]

        if logicalAddress not in self.logicalAddresses:
            self.logicalAddresses.append(logicalAddress)

    def add_component(self, id, *description):
        """Add a unique dict representing TAK-info to instance."""

        component = {
            "hsaId": id
        }

        if description:
            component["beskrivning"] = description[0]

        if component not in self.components:
            self.components.append(component)

    def add_contract(self,
                     namespace,
                     *description):
        """Add a unique dict representing TAK-info to instance."""

        ix = namespace.rfind(":") + 1
        majorStr = namespace[ix:]
        major = int(majorStr)

        contract = {
            "namnrymd": namespace,
            "majorVersion": major
        }
        if description:
            contract["beskrivning"] = description[0]

        if contract not in self.contracts:
            self.contracts.append(contract)


    def add_authorization(self,
                          component: object,
                          logicalAddress: object,
                          namespace: object
                          ) -> object:
        """Add a unique dict representing TAK-info to instance."""

        auth = {
            "tjanstekonsument": component,
            "logiskAdress": logicalAddress,
            "tjanstekontrakt": namespace
        }

        if auth not in self.authorities:
            self.authorities.append(auth)


    def add_routing(self,
                    component: object,
                    address: object,
                    logicalAddress: object,
                    namespace: object,
                    rivtaProfile: object = "RIVTABP21") -> object:
        """Add a unique dict representing TAK-info to instance."""

        routing = {
            "tjanstekomponent": component,
            "logiskAdress": logicalAddress,
            "tjanstekontrakt": namespace,
            "rivtaprofil": rivtaProfile
        }

        if address:
            routing["adress"] = address

        if routing not in self.routings:
            self.routings.append(routing)

    def get_json(self):
        """Return the information in this section instance in the form of a dict"""

        return {
            "tjanstekomponenter": self.components,
            "tjanstekontrakt": self.contracts,
            "logiskadresser": self.logicalAddresses,
            "anropsbehorigheter": self.authorities,
            "vagval": self.routings,
        }

