# -*- coding: utf-8 -*-

import unittest

from .populate import loopOdata, extract
from geojson import Feature

class TestScrapeMethods(unittest.TestCase):

    def test_scrape(self):
        """ """
        rec = next(loopOdata())
        self.assertTrue(isinstance(rec, dict))

class TestExtracetMethods(unittest.TestCase):

    def test_extract(self):
        nrecs = 10
        recs = extract(nrecs)

        try:
            feat = next(recs)
        except StopIteration:
            self.fail("Please increase the test 'nrecs' parameter!")

        self.assertTrue(isinstance(feat, Feature))

if __name__ == '__main__':
    # import argparse
    #
    # parser = argparse.ArgumentParser(description='Test some methods.')
    #
    # parser.add_argument("-r", "--recs",
    #     help = 'Records to extract for test',
    #     type=int, default=10,
    # )
    #
    # args = parser.parse_args()

    unittest.main()
