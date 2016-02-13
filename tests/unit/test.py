import unittest


class DescriptionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_test(self):
        self.assertEqual(0, 0)

    def tearDown(self):
        pass


class GschemRenderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_test(self):
        self.assertEqual(0, 0)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
