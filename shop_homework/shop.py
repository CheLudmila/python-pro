"""Проста система магазину. Запуск: python shop_homework/shop.py."""

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


def check_quantity(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"Кількість має бути цілим числом не менше {minimum}.")


class Product:
    def __init__(self, name, category, price):
        self.name = name
        self.category = category
        self.change_price(price)

    def change_price(self, new_price):
        """Встановити нову ціну. Decimal забезпечує точність грошових сум."""
        try:
            price = Decimal(str(new_price))
        except InvalidOperation:
            raise ValueError("Ціна має бути числом.") from None
        if not price.is_finite() or price < 0:
            raise ValueError("Ціна має бути скінченним невід'ємним числом.")
        self.price = price


class Inventory:
    """Залишки товарів на одному складі, окремо від характеристик товару."""

    def __init__(self):
        self.quantities = {}

    def get_quantity(self, product):
        return self.quantities.get(product, 0)

    def change_quantity(self, product, new_quantity):
        """Встановити новий залишок на складі (не додати до попереднього)."""
        check_quantity(new_quantity)
        self.quantities[product] = new_quantity

    def remove_product(self, product, quantity):
        check_quantity(quantity, minimum=1)
        available = self.get_quantity(product)
        if quantity > available:
            raise ValueError(f"Недостатньо товару «{product.name}» на складі.")
        self.change_quantity(product, available - quantity)


class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.orders = []

    def add_order(self, order):
        if order not in self.orders:
            self.orders.append(order)


class Order:
    def __init__(self, inventory):
        self.inventory = inventory
        # Кожна позиція: товар, замовлена кількість, ціна на момент додавання.
        self.products = []
        self.total_amount = Decimal("0")

    def add_product(self, product, quantity=1):
        """Одразу списати товар зі складу та додати його до замовлення."""
        self.inventory.remove_product(product, quantity)
        self.products.append((product, quantity, product.price))
        self.calculate_total()

    def calculate_total(self):
        self.total_amount = sum(
            (quantity * price for product, quantity, price in self.products),
            Decimal("0"),
        )
        return self.total_amount


class Store:
    def __init__(self):
        self.products = []
        self.customers = []
        self.inventory = Inventory()

    @classmethod
    def from_file(cls, filename):
        """Прочитати TXT у кодуванні UTF-8 з роздільником ;."""
        store = cls()
        with open(filename, encoding="utf-8-sig", newline="") as file:
            for line_number, row in enumerate(csv.reader(file, delimiter=";"), 1):
                if not row or not any(field.strip() for field in row):
                    continue
                if row[0].lstrip().startswith("#"):
                    continue
                row = [field.strip() for field in row]
                try:
                    if row[0] == "product" and len(row) == 5:
                        _, name, category, price, quantity = row
                        if not name or not category:
                            raise ValueError("Назва та категорія не можуть бути порожніми.")
                        product = Product(name, category, price)
                        store.inventory.change_quantity(product, int(quantity))
                        store.products.append(product)
                    elif row[0] == "customer" and len(row) == 3:
                        _, name, email = row
                        if not name or not email:
                            raise ValueError("Ім'я та пошта не можуть бути порожніми.")
                        store.customers.append(Customer(name, email))
                    else:
                        raise ValueError("Невідомий тип запису або неправильна кількість полів.")
                except ValueError as error:
                    raise ValueError(f"Рядок {line_number}: {error}") from error
        return store


def main():
    # Шлях залежить від розташування скрипту, а не поточної папки термінала.
    filename = Path(__file__).with_name("store.txt")
    try:
        store = Store.from_file(filename)
        print("Товари магазину:")
        for product in store.products:
            print(f"{product.name}: {product.price:.2f} грн, залишок: {store.inventory.get_quantity(product)}")

        if not store.products or not store.customers:
            print("Для демонстрації потрібні хоча б один товар і один клієнт.")
            return

        product = store.products[0]
        customer = store.customers[0]
        order = Order(store.inventory)
        order.add_product(product, 2)
        customer.add_order(order)

        print(f"\nЗамовлення клієнта {customer.name} ({customer.email}):")
        for item, quantity, price in order.products:
            print(f"{item.name}: {quantity} шт. x {price:.2f} грн")
        print(f"Загальна сума: {order.calculate_total():.2f} грн")
        print(f"Залишок товару «{product.name}»: {store.inventory.get_quantity(product)}")
    except (OSError, ValueError) as error:
        print(f"Помилка: {error}")


if __name__ == "__main__":
    main()
