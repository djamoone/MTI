# class Printer:
#     def print_document(self, document):
#         pass
#     def scan_document(self, document):
#         pass
#     def fax_document(self, document):
#         pass
# class BasicPrinter(Printer):
#     def print_document(self, document):
#         print(f"Printing: {document}")
#     def scan_document(self, document):
#         # Unnecessary method for BasicPrinter
#         raise NotImplementedError("This printer cannot scan.")
#     def fax_document(self, document):
#         # Unnecessary method for BasicPrinter
#         raise NotImplementedError("This printer cannot fax.")


# Separate Interfaces
class Printable:
    def print_document(self, document):
        pass
class Scannable:
    def scan_document(self, document):
        pass
class Faxable:
    def fax_document(self, document):
        pass
# Implementing Classes
class BasicPrinter(Printable):
    def print_document(self, document):
        print(f"Printing: {document}")

class AdvancedPrinter(Printable, Scannable, Faxable):
    def print_document(self, document):
        print(f"Printing: {document}")
    def scan_document(self, document):
        print(f"Scanning: {document}")
    def fax_document(self, document):
        print(f"Faxing: {document}")


if __name__ == '__main__':
    # basic_printer = BasicPrinter()
    # basic_printer.print_document("Document2.pdf")
    # basic_printer.scan_document("Document2.pdf")
    # basic_printer.fax_document("Document2.pdf")