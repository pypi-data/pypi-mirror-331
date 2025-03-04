import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
import aemo_to_tariff.sapower as sapower

class TestSAPower(unittest.TestCase):
    def test_some_sapower_functionality(self):
        interval_time = datetime(2025, 2, 20, 9, 10, tzinfo=ZoneInfo('Australia/Adelaide'))
        tariff_code = 'RTOU'
        rrp = -100.0
        expected_price = 10.26535477
        price = sapower.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.1678, expected_price, places=1)

    def test_later_day(self):
        interval_time = datetime(2025, 2, 20, 15, 10, tzinfo=ZoneInfo('Australia/Adelaide'))
        tariff_code = 'RTOU'
        rrp = -76.53
        expected_price = 13.03587882
        price = sapower.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.1678, expected_price, places=1)
    
    def test_two_way_tou_peak(self):
        interval_time = datetime(2025, 2, 20, 18, 10, tzinfo=ZoneInfo('Australia/Adelaide'))
        tariff_code = 'RELE2W'
        rrp = -76.53
        expected_price = 29.705328600000005
        price = sapower.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.1678, expected_price, places=1)
    
    def test_two_way_tou_feed_peak(self):
        interval_time = datetime(2025, 2, 20, 18, 10, tzinfo=ZoneInfo('Australia/Adelaide'))
        tariff_code = 'RELE2W'
        rrp = 100
        expected_price = 22.36
        price = sapower.convert_feed_in_tariff(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=1)
    
    def test_two_way_tou_feed_off_peak(self):
        interval_time = datetime(2025, 2, 20, 13, 10, tzinfo=ZoneInfo('Australia/Adelaide'))
        tariff_code = 'RELE2W'
        rrp = 100
        expected_price = 10.0
        price = sapower.convert_feed_in_tariff(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=1)