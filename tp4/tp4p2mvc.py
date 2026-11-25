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

def controller():
    # This program allows you to search the number
    # in a table by its name, and display
    # read data from the keyboard
    data_model = model()
    myviewer = view()
    """ search a name """
    name = myviewer.input()
    persons = data_model.search(name)
    myviewer.output(persons)
if __name__ == '__main__':
    controller()