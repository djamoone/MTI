
import sys


class model_file:
    """Data Model class"""

    def __init__(self):
        self.directory = []

        try:
            myfile = open("directory.txt", "r")
        except:
            print("Can't open DataFile")
            sys.exit()

        lines = myfile.readlines()

        for line in lines:
            line = line.strip('\n')

            if line:
                fields = line.split('\t')

                person = {}
                person["familyname"] = fields[0]
                person["firstname"] = fields[1]
                person["tel"] = fields[2]

                self.directory.append(person)

        myfile.close()

    def __del__(self):
        """Save data in the file when the object is destroyed"""

        try:
            myfile = open("directory.txt", "w")
        except:
            print("Can't open DataFile")
            return

        for person in self.directory:
            line = "\t".join([
                person['familyname'],
                person['firstname'],
                person['tel']
            ])

            line += "\n"
            myfile.write(line)

        myfile.close()

    def search(self, nom):
        """Search for people by family name"""

        persons = []

        for person in self.directory:
            if person["familyname"].lower() == nom.lower():
                persons.append(person)

        return persons

    def get_all(self):
        """Return all people"""

        persons = []

        for person in self.directory:
            persons.append(person)

        return persons

    def add(self, name, firstname, tel):
        """Add a person"""

        person = {}

        person["familyname"] = name
        person["firstname"] = firstname
        person["tel"] = tel

        self.directory.append(person)

        return "Person added successfully"
