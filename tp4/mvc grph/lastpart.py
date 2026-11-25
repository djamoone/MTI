
from tkinter import Tk, Label, Button, END, W, E, Text
from model_file import model_file


class view_tk:

    def __init__(self, model):

        master = Tk()

        self.master = master

        # Use the model passed by the controller
        self.model = model

        master.title("Directory")

        # =========================
        # LABELS
        # =========================

        self.label = Label(master, text="Family Name:")
        self.label_firstname = Label(master, text="First Name:")
        self.label_tel = Label(master, text="Tel:")

        self.output_label = Label(master, text="Output")

        # =========================
        # INPUT FIELDS
        # =========================

        self.entry = Text(master, height=1, width=20)

        self.entry_firstname = Text(master, height=1, width=20)

        self.entry_tel = Text(master, height=1, width=20)

        self.output = Text(master, height=10, width=60)

        # =========================
        # BUTTONS
        # =========================

        self.search_button = Button(
            master,
            text="Search",
            command=lambda: self.update("search")
        )

        self.add_button = Button(
            master,
            text="Add",
            command=lambda: self.update("add")
        )

        self.all_button = Button(
            master,
            text="Get All",
            command=lambda: self.update("get_all")
        )

        # =========================
        # LAYOUT
        # =========================

        self.label.grid(row=0, column=0, sticky=W)
        self.label_firstname.grid(row=0, column=1, sticky=W)
        self.label_tel.grid(row=0, column=2, sticky=W)

        self.entry.grid(row=1, column=0, sticky=W+E)
        self.entry_firstname.grid(row=1, column=1, sticky=W+E)
        self.entry_tel.grid(row=1, column=2, sticky=W+E)

        self.search_button.grid(row=2, column=0)
        self.add_button.grid(row=2, column=1)
        self.all_button.grid(row=2, column=2)

        self.output_label.grid(row=3, column=0, sticky=W)

        self.output.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky=W+E
        )

        # Allow columns to expand
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)

    # =========================
    # UPDATE
    # =========================

    def update(self, method):

        familyname = self.entry.get("1.0", END).strip()

        firstname = self.entry_firstname.get("1.0", END).strip()

        tel = self.entry_tel.get("1.0", END).strip()

        if method == "search":

            result = self.search(familyname)

        elif method == "add":

            result = self.add(familyname, firstname, tel)

        elif method == "get_all":

            result = self.get_all()

        else:

            result = "Unknown method"

        # Clear previous output
        self.output.delete("1.0", END)

        # Display new result
        self.output.insert(END, str(result))

    # =========================
    # MODEL METHODS
    # =========================

    def add(self, familyname, firstname, tel):

        return self.model.add(familyname, firstname, tel)

    def search(self, familyname):

        result = self.model.search(familyname)

        if result:
            return result

        else:
            return "'%s' not found" % familyname

    def get_all(self):

        return self.model.get_all()

    # =========================
    # RUN GUI
    # =========================

    def run(self):

        self.master.mainloop()


# =========================
# CONTROLLER
# =========================

def controller3():

    data_model = model_file()

    my_viewer = view_tk(data_model)

    my_viewer.run()


if __name__ == "__main__":

    controller3()
