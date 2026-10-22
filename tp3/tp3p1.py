# class Order:
#     def __init__(self, items):
#         self.items = items
#     def calculate_total(self):
#         return sum(item['price'] for item in self.items)
#     def print_order(self):
#         print("Order details:")
#         for item in self.items:
#             print(f"{item['name']}: ${item['price']}")
#     def save_to_db(self):
#         print("Saving order to database...")

class Order:
    def __init__(self, items):
        self.items = items

    def calculate_total(self):
        return sum(item['price'] for item in self.items)


class OrderPrinter:
    def print_order(self, order):
        print("Order details:")
        for item in order.items:
            print(f"{item['name']}: ${item['price']}")


class OrderRepository:
    def save_to_db(self, order):
        print("Saving order to database...")

# class Discount:
#     def __init__(self, customer, price):
#         self.customer = customer
#         self.price = price
#     def apply_discount(self):
#         if self.customer == 'VIP':
#             return self.price * 0.8 # 20% discount
#         return self.price

class Discount:
    def __init__(self, price):
        self.price = price
    def apply_discount(self):
        return self.price
class VIPDiscount(Discount):
    def apply_discount(self):
        return self.price * 0.8 # 20% discount

class FirstTimeCustomerDiscount(Discount):
    def apply_discount(self):
        return self.price * 0.9  # 10% discount


if __name__ == '__main__':
    products = [
        {"name": "fruit", "price": 50},
        {"name": "vegetables", "price": 100},
        {"name": "Bread", "price": 20},
        {"name": "Meat", "price": 1000},
    ]

    # Order
    my_order = Order(products)
    total = my_order.calculate_total()
    print("Total order:", total, "$")

    printer = OrderPrinter()
    printer.print_order(my_order)

    repository = OrderRepository()
    repository.save_to_db(my_order)

    # Regular customer
    price = 1000
    customer = "Regular"
    discount = Discount(price)
    newprice = discount.apply_discount()
    print(f"Old Price: ${price} for {customer}, New Price: ${newprice}")

    # VIP customer
    customer = "VIP"
    vip = VIPDiscount(price)
    newprice = vip.apply_discount()
    print(f"Old Price: ${price} for {customer}, New Price: ${newprice}")

    # First-time customer
    customer = "First-time"
    first_time = FirstTimeCustomerDiscount(price)
    newprice = first_time.apply_discount()
    print(f"Old Price: ${price} for {customer}, New Price: ${newprice}")
