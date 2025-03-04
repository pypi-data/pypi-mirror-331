import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from aemo_to_tariff.ausgrid import convert_feed_in_tariff, time_zone

class TestAusgrid(unittest.TestCase):
    def test_feed_ausgrid_functionality(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 100.0)
        self.assertAlmostEqual(feed_in_price, 10.00, places=1)
