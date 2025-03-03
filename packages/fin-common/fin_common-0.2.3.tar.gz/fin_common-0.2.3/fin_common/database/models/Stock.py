class Stock:
    def __init__(self, ticker, name, sector):
        self.ticker = ticker
        self.name = name
        self.sector = sector

    @staticmethod
    def from_dict(data):
        return Stock(
            ticker=data.get("ticker"),
            name=data.get("name"),
            sector=data.get("sector")
        )
    
    def to_dict(self):
        return {
            "ticker": self.ticker,
            "name": self.name,
            "sector": self.sector
        }

class Holding:
    def __init__(self, stock, quantity, average_buy_price, purchase_date):
        self.stock: Stock = stock
        self.quantity = quantity
        self.average_buy_price = average_buy_price
        self.purchase_date = purchase_date

    @staticmethod
    def from_dict(data):
        return Holding(
            stock=Stock.from_dict(data.get("stock")),
            quantity=data.get("quantity"),
            average_buy_price=data.get("average_buy_price"),
            purchase_date=data.get("purchase_date")
        )
    
    def to_dict(self):
        return {
            "stock": self.stock.to_dict(),
            "quantity": self.quantity,
            "average_buy_price": self.average_buy_price,
            "purchase_date": self.purchase_date
        }


class Transaction:
    def __init__(self, stock, quantity, price, transaction_type, transaction_date):
        self.stock: Stock = stock
        self.quantity = quantity
        self.price = price
        self.transaction_type = transaction_type
        self.transaction_date = transaction_date

    @staticmethod
    def from_dict(data):
        return Transaction(
            stock=Stock.from_dict(data.get("stock")),
            quantity=data.get("quantity"),
            price=data.get("price"),
            transaction_type=data.get("transaction_type"),
            transaction_date=data.get("transaction_date")
        )
    
    def to_dict(self):
        return {
            "stock": self.stock.to_dict(),
            "quantity": self.quantity,
            "price": self.price,
            "transaction_type": self.transaction_type,
            "transaction_date": self.transaction_date
        }

    