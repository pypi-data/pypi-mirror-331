import os
import shutil
import sys
import unittest
from horhor.bin.horhor import main as horhor_main


class TesthorhorStart(unittest.TestCase):
    CURR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEST_DIR = os.path.join(CURR_DIR, "testproject-unittest")

    def setup(self):
        # Clean/create directory to start into
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)
        os.mkdir(self.TEST_DIR)

    def cleanup(self):
        # Cleanup
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)

    def test_help(self):
        # Set args
        sys.argv = ["horhor", "help"]
        # Run
        horhor_main()
        # Nothing to assert here... just make sure it doesn't error out.

    def test_help_start(self):
        # Set args
        sys.argv = ["horhor", "help", "start"]
        # Run
        horhor_main()
        # Nothing to assert here... just make sure it doesn't error out.

    def test_default(self):
        self.setup()
        # Set args
        sys.argv = ["horhor", "start", "myproject", self.TEST_DIR]
        # Run
        horhor_main()
        # Assert files exist
        self.assertTrue(
            os.path.exists(os.path.join(self.TEST_DIR, "README.md"))
        )
        self.cleanup()

    def test_allopts(self):
        self.setup()
        # Set args
        sys.argv = [
            "horhor",
            "start",
            "myproject",
            self.TEST_DIR,
            "--template",
            "basic",
            "--sitename",
            "MegaCorp, Inc.",
            "--domain",
            "example.com",
        ]
        # Run
        horhor_main()
        # Assert files exist
        self.assertTrue(
            os.path.exists(os.path.join(self.TEST_DIR, "README.md"))
        )
        self.cleanup()

    def test_domain_www(self):
        self.setup()
        # Set args
        sys.argv = [
            "horhor",
            "start",
            "myproject",
            self.TEST_DIR,
            "--domain",
            "www.example.com",
        ]
        # Run
        horhor_main()
        # Assert files exist
        self.assertTrue(
            os.path.exists(os.path.join(self.TEST_DIR, "README.md"))
        )
        self.cleanup()

    def test_template_pro(self):
        self.setup()
        # Set args
        sys.argv = [
            "horhor",
            "start",
            "myproject",
            self.TEST_DIR,
            "--template",
            "pro",
        ]
        # Run
        horhor_main()
        # Assert files exist
        self.assertTrue(
            os.path.exists(os.path.join(self.TEST_DIR, "README.md"))
        )
        self.cleanup()
