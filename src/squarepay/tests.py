from django.test import TestCase
from django.conf import settings
from datetime import datetime

from .cokelog import CokeLog

class ParseCokeLog(TestCase):
    def test_parse_cokelog(self):
        fn = getattr(settings, 'COKELOG_PATH', None)
        if fn is None:
            return

        cokelog = CokeLog()
        self.assertFalse(cokelog.is_loaded())
        cokelog.open()
        self.assertTrue(cokelog.is_loaded())

        self.assertIsInstance(cokelog.dispenses, dict)
        for key, val in cokelog.dispenses.items():
            self.assertIsInstance(val, (list, tuple))
            for record in val:
                self.assertIsInstance(record, dict)
                self.assertTrue('by' in record)
                self.assertTrue('item' in record)
                self.assertIsInstance(record['date'], datetime)

        n = len(cokelog.dispenses)
        cokelog.reload()
        self.assertTrue(n == len(cokelog.dispenses))
