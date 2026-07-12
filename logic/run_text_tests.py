import os
from texttests.text_test_runner import TextTestRunner

if __name__ == "__main__":
    folder = os.path.join(os.path.dirname(__file__), "tests", "integration")
    TextTestRunner().run_all(folder)
