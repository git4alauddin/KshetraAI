import unittest

from demo.scripts.run_acceptance_checks import (
    has_acceptance_failures,
    run_acceptance_checks,
)


class Build10AcceptanceChecksTest(unittest.TestCase):
    def test_acceptance_checks_pass_for_committed_demo_artifacts(self):
        checks = run_acceptance_checks()

        self.assertFalse(has_acceptance_failures(checks))
        self.assertTrue(all(check.status == "PASS" for check in checks))


if __name__ == "__main__":
    unittest.main()
