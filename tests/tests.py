import unittest

if __name__ == "__main__":
    # Main file that runs all the tests in this folder.
    testsuite = unittest.TestLoader().discover(".")
    unittest.TextTestRunner(verbosity=1).run(testsuite)
