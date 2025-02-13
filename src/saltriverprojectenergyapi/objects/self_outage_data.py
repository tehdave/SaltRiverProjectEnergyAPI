class SelfOutageData:
    def __init__(self, isInOutageArea, estimatedRestorationTime, reportedOutageTime, estimatedUsersImpacted):
        self.isInOutageArea = isInOutageArea
        self.estimatedRestorationTime = estimatedRestorationTime
        self.reportedOutageTime = reportedOutageTime
        self.estimatedUsersImpacted = estimatedUsersImpacted

    def __repr__(self):
        return (
            f"isInOutageArea={self.isInOutageArea},"
            f"estimatedRestorationTime={self.estimatedRestorationTime},"
            f"reportedOutageTime={self.reportedOutageTime},"
            f"estimatedUsersImpacted={self.estimatedUsersImpacted}"
        )