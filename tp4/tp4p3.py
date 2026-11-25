

class model:
    """data model class"""
    def __init__(self) :
        self.directory=[
            {"firstname":'Ahmed', "familyname":'Mahdi', 'tel':'0778787887'},
            {"firstname":'Mohamed', "familyname":'Mahdi','tel':'0778787887'},
            {"firstname":'Mounir', "familyname":'Katibi','tel':'0778787887'},
            {"firstname":'Noui', "familyname":'Brahimi','tel':'0778787887'}
            ]
    def search(self,nom):
        """lookup for a tel by lastname"""
        #found people list
        persons = []
        for persn in self.directory:
            #show all people with the given name
            if persn["familyname"]==nom:
                persons.append(persn)
        return persons

    def get_all(self):
            """ Find a tel by name"""
            # List of found people
            persons = []
            for persn in self.directory:
            # display all people
                persons.append(persn)
            # a table with field names
            return persons
    
    def add(self, name, firstname, tel):
        """ Add a person """
        person ={}
        person["familyname"] = name
        person["firstname"] = firstname
        person["tel"] = tel
        self.directory.append(person)

class view:
    def __init__(self) :
        pass
    def input(self):
        """retrieve thename to search for"""
        print('finding a phone')
        print('give a name')
        name=input()
        return name
    def output(self,persons):
        """display informatiion from a lilst of persons"""
        print('list of found names')
        print("%d found people "%len(persons))
        for pers in persons:
            print(pers['familyname'],pers['firstname'],pers['tel'])

    def input_add(self,):
        """get name to add"""
        print("Add a person")
        print("Give a name")
        name = input()
        print("Give a firstname")
        firstname = input()
        print("Give a firstname")
        tel = input()
        return (name, firstname, tel)

class controller:
    def __init__(self,):
        """ controller constrctor"""
        # init data model
        self.data_model = model()
        #self.data_model = model_file()
        self.viewer = view()
    def search(self):
        """ search a name """
        name = self.viewer.input()
        persons = self.data_model.search(name)
        self.viewer.output(persons)

    def add(self):
        """ Add a new name """
        name, firstname, tel = self.viewer.input_add()
        self.data_model.add(name, firstname, tel)
        persons = self.data_model.get_all()
        self.viewer.output(persons)
        tel = input()
        return( name, firstname, tel)
if __name__ == '__main__':
    contro = controller()

    k = input('Number of people to add: ')

    while not k.isdigit():
        k = input('Enter a valid number: ')

    k = int(k)
    
    for i in range(k):
        contro.add()
        
