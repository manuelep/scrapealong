# -*- coding: utf-8 -*-

import unittest

from .populate import loopOdata, fetch, populate, db
from geojson import Feature
nrecs = 50

class TestScrapeMethods(unittest.TestCase):

    def test_scrape(self):
        """ """
        rec = next(loopOdata())
        self.assertTrue(isinstance(rec, dict))

class TestExtracetMethods(unittest.TestCase):

    def setUp(self):
        populate()
        # db.commit()

    def test_fetch(self):
        recs = fetch(nrecs)

        try:
            feat = next(recs)
        except StopIteration:
            self.fail("Please increase the test 'nrecs' parameter!")
        else:
            db.commit()


        self.assertTrue(isinstance(feat, Feature))

if __name__ == '__main__':
    unittest.main()
