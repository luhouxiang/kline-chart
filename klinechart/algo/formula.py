

# %% 公式
# //////////////////////////////////////////////////////////////////////////////
class MA:
    def __init__(self, e0=5):
        self.e0 = e0
        self.ma, self.malist = 0, []
        self.name = f"{self.__class__.__name__}{self.e0}"

    def input(self, price):
        self.malist.append(price)
        self.malist = self.malist[-self.e0:]
        self.ma = sum(self.malist) / len(self.malist)


class EMA:
    """Simple stateful EMA helper reused by indicators such as MACD."""

    def __init__(self, period: int):
        self.period = period
        self.alpha = 2 / (period + 1)
        self.name = f"{self.__class__.__name__}{self.period}"
        self.ema = None


    def input(self, price: float) -> float:
        if self.ema is None:
            self.ema = price
        else:
            self.ema = (price - self.ema) * self.alpha + self.ema
        return self.ema
# //////////////////////////////////////////////////////////////////////////////
