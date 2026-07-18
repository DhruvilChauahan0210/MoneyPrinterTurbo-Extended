import csv
import os
import tempfile
import unittest

from channel_optimizer import analyze


class TestChannelOptimizer(unittest.TestCase):
    def test_separates_reach_from_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "Table data.csv")
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow([
                    "Content", "Video title", "Video publish time", "Duration", "Views",
                    "Watch time (hours)", "Subscribers", "Impressions",
                    "Impressions click-through rate (%)",
                ])
                writer.writerow(["Total", "", "", "", 11000, 10, 12, 0, 0])
                writer.writerow(["reach", "Haaland controversy", "", 13, 10000, 8, 1, 0, 0])
                writer.writerow(["loyalty", "Thank You Ronaldo", "", 40, 1000, 2, 11, 0, 0])

            report = analyze(path)

        self.assertEqual(report["top_reach"][0]["role"], "reach_winner")
        self.assertEqual(report["top_conversion"][0]["role"], "loyalty_winner")


if __name__ == "__main__":
    unittest.main()
