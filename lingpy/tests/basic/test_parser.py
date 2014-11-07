import os
from unittest import TestCase

from lingpy.tests.util import test_data


class TestParser(TestCase):
    def setUp(self):
        from lingpy.basic.parser import QLCParser

        self.parser = QLCParser(test_data('KSL.qlc'))

    def test_cache(self):
        from lingpy.basic.parser import QLCParser
        from lingpy.cache import path

        filename = 'lingpy_test.qlc'
        self.parser.pickle(filename=filename)
        from_cache = QLCParser(filename)
        self.assertEqual(self.parser.header, from_cache.header)
        os.remove(str(path(filename)))

    def test_len(self):
        assert len(self.parser)

    def test_add_entries(self):
        # shouldn't this raise an exception?
        self.parser.add_entries('', 'taxon', lambda t: t.lower())

        # shouldn't this call work?
        #self.parser.add_entries('lTaxon', 'taxon', lambda t: t.lower(), override=True)

        self.parser.add_entries('lTaxon', 'taxon', lambda t: t.lower())
