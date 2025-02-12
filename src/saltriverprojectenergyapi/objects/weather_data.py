class WeatherData:
    def __init__(self, date, high, low, average):
        self.date = date
        self.high = high
        self.low = low
        self.average = average
        
    def __repr__(self):
        return (
            f"date={self.date},"
            f"high={self.high},"
            f"low={self.low},"
            f"average={self.average}"
        )