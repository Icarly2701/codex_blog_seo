import unittest

from app.services.usage import UsageState, can_generate, increment_count, remaining_quota


class UsageServiceTests(unittest.TestCase):
    def test_monthly_limit_blocks_after_three_generations(self) -> None:
        state = UsageState(count=0, limit=3)

        self.assertTrue(can_generate(state))
        state = increment_count(state)
        self.assertEqual(remaining_quota(state), 2)

        self.assertTrue(can_generate(state))
        state = increment_count(state)
        self.assertEqual(remaining_quota(state), 1)

        self.assertTrue(can_generate(state))
        state = increment_count(state)
        self.assertEqual(remaining_quota(state), 0)

        self.assertFalse(can_generate(state))


if __name__ == "__main__":
    unittest.main()
