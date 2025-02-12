class HourlyUsage:
    def __init__(self, date, hour, onPeakKwh, offPeakKwh, shoulderKwh, superOffPeakKwh, totalKwh, 
                 onPeakCost, offPeakCost, shoulderCost, superOffPeakCost, totalCost):
        self.date = date
        self.hour = hour
        self.onPeakKwh = onPeakKwh
        self.offPeakKwh = offPeakKwh
        self.shoulderKwh = shoulderKwh
        self.superOffPeakKwh = superOffPeakKwh
        self.totalKwh = totalKwh
        self.onPeakCost = onPeakCost
        self.offPeakCost = offPeakCost
        self.shoulderCost = shoulderCost
        self.superOffPeakCost = superOffPeakCost
        self.totalCost = totalCost

    def __repr__(self):
        return (
            f"EnergyData(date={self.date},"
            f"hour={self.hour},"
            f"onPeakKwh={self.onPeakKwh},"
            f"offPeakKwh={self.offPeakKwh},"
            f"shoulderKwh={self.shoulderKwh},"
            f"superOffPeakKwh={self.superOffPeakKwh},"
            f"totalKwh={self.totalKwh},"
            f"onPeakCost={self.onPeakCost},"
            f"offPeakCost={self.offPeakCost},"
            f"shoulderCost={self.shoulderCost},"
            f"superOffPeakCost={self.superOffPeakCost},"
            f"totalCost={self.totalCost})")