from abc import ABC, abstractmethod


class Compte(ABC):
    def __init__(self, username: str):
        self.username = username

    @abstractmethod
    def stock(self):
        pass

    @abstractmethod
    def achat(self):
        pass

    @abstractmethod
    def commande(self):
        pass


class Gestionnaire(Compte):
    def stock(self):
        print(f"[{self.username}] Managing stock.")

    def achat(self):
        print(f"[{self.username}] Making purchase.")

    def commande(self):
        print(f"[{self.username}] Placing order.")

    def voir_recettes_totales(self):
        print(f"[{self.username}] Viewing total income.")


class Vendeur(Compte):
    def stock(self):
        print(f"[{self.username}] Viewing stock for sales.")

    def achat(self):
        print(f"[{self.username}] Making purchase.")

    def commande(self):
        print(f"[{self.username}] Placing order.")

    def vendre(self):
        print(f"[{self.username}] Selling items to customers.")


class Visiteur(Compte):
    def stock(self):
        print(f"[{self.username}] Viewing available stock.")

    def achat(self):
        print(f"[{self.username}] Making purchase.")

    def commande(self):
        print(f"[{self.username}] Placing order.")


class CompteFactory(ABC):
    @abstractmethod
    def createCompte(self, account_type: str, username: str) -> Compte:
        pass


class ConcreteCompteFactory(CompteFactory):
    def createCompte(self, account_type: str, username: str) -> Compte:
        role = account_type.lower()
        if role in ("gestionnaire", "manager"):
            return Gestionnaire(username)
        elif role in ("vendeur", "seller"):
            return Vendeur(username)
        elif role in ("visiteur", "visitor"):
            return Visiteur(username)
        else:
            raise ValueError(f"Unknown account type: {account_type}")


if __name__ == "__main__":
    factory = ConcreteCompteFactory()

    manager = factory.createCompte("manager", "alice")
    seller = factory.createCompte("seller", "bob")
    visitor = factory.createCompte("visitor", "charlie")

    manager.stock()
    manager.voir_recettes_totales()

    seller.stock()
    seller.vendre()

    visitor.stock()
    visitor.commande()