import yfinance as y

class ManagePriceStock:
    def __init__(self, symbol):
        self.symbol = symbol


    def get_price(self):
        stock = y.Ticker(self.symbol)
        data = stock.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[0]
            return price
        else:
            return None