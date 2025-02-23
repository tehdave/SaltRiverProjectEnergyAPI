"""Define various dataclass objects we will use."""
from dataclasses import asdict, dataclass, is_dataclass
from typing import List


@dataclass
class CostData:
    """A class to represent Cost data."""

    on_peak_cost: float
    off_peak_cost: float
    shoulder_cost: float
    super_off_peak_cost: float
    total_cost: float

@dataclass
class KwhData:
    """A class to represent KWH data."""

    on_peak_kwh: float
    off_peak_kwh: float
    shoulder_kwh: float
    super_off_peak_kwh: float
    total_kwh: float

@dataclass
class HourlyUsage:
    """A class to represent hourly energy usage and cost data."""

    date: str
    hour: int
    kwh_data: KwhData
    cost_data: CostData

    def __repr__(self):
        """Return a string representation of the HourlyUsage object.

        The string representation includes the date, hour, kwh_data, and cost_data
        attributes of the HourlyUsage object.

        Returns:
            str: A string representation of the HourlyUsage object.

        """
        kwh_repr = asdict(self.kwh_data) if is_dataclass(self.kwh_data) else \
            self.kwh_data
        cost_repr = asdict(self.cost_data) if is_dataclass(self.cost_data) else \
            self.cost_data

        return (
            f"HourlyUsage(date={self.date}, hour={self.hour}, "
            f"kwh_data={kwh_repr}, cost_data={cost_repr})"
        )

@dataclass
class EnergyUsageData:
    """A class to represent energy usage data."""

    energy_usage: List[HourlyUsage]

@dataclass
class SelfOutageData:
    """A class to represent self outage data."""

    is_in_outage_area: bool
    extimated_restoration_time: str
    reported_outage_time: str
    estimated_users_impacted: int

@dataclass
class WeatherData:
    """A class to represent weather data."""

    date: str
    high: float
    low: float
    average: float

@dataclass
class RateMetaData:
    """A class to represent SRP Account Rate data."""

    description: str
    short_description: str
    price_plan_url: str
    is_demand: bool
    is_metered: bool
    is_solar: bool
