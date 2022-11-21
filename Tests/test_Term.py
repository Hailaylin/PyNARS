import unittest


class TEST_Term(unittest.TestCase):
    def test_0(self):
        from pynars.Narsese import Term
        t = Term("0")
        pass

        

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Term
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
