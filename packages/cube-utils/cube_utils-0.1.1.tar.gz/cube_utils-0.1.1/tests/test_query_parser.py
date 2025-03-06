import unittest
from cube_utils.query_parser import extract_cubes, extract_members


class TestExtractCubes(unittest.TestCase):

    def test_extract_cubes_with_all_fields(self):
        payload = {
            "dimensions": ["test_a.city", "test_a.country", "test_a.state"],
            "measures": ["test_b.count"],
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ],
            "segments": ["test_d.us_segment"],
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ],
        }
        expected_cubes = ["test_a", "test_b", "test_c", "test_d"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_complex_boolean_logic(self):
        payload = {
            "segments": [],
            "filters": [
                {
                    "or": [
                        {
                            "and": [
                                {
                                    "values": ["Corpus Christi"],
                                    "member": "test_a.city",
                                    "operator": "equals",
                                },
                                {
                                    "member": "test_b.age_bucket",
                                    "operator": "equals",
                                    "values": ["Senior adult"],
                                },
                            ]
                        },
                        {
                            "member": "test_c.city",
                            "operator": "equals",
                            "values": ["Sacramento"],
                        },
                    ]
                },
                {"or": [{"member": "test_d.city", "operator": "set"}]},
            ],
        }
        expected_cubes = ["test_a", "test_b", "test_c", "test_d"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_dimensions_only(self):
        payload = {"dimensions": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_cubes = ["test_a"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_measures_only(self):
        payload = {"measures": ["test_b.count"]}
        expected_cubes = ["test_b"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_filters_only(self):
        payload = {
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ]
        }
        expected_cubes = ["test_a"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_segments_only(self):
        payload = {"segments": ["test_a.us_segment"]}
        expected_cubes = ["test_a"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_timeDimensions_only(self):
        payload = {
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ]
        }
        expected_cubes = ["test_c"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_empty_payload(self):
        payload = {}
        expected_cubes = []
        self.assertEqual(extract_cubes(payload), expected_cubes)

    def test_extract_cubes_with_invalid_keywords(self):
        payload = {"invalid": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_cubes = []
        self.assertEqual(extract_cubes(payload), expected_cubes)


class TestExtractMembers(unittest.TestCase):

    def test_extract_members_with_all_fields(self):
        payload = {
            "dimensions": ["test_a.city", "test_a.country", "test_a.state"],
            "measures": ["test_b.count"],
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ],
            "segments": ["test_d.us_segment"],
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ],
        }
        expected_members = [
            "test_a.city",
            "test_a.country",
            "test_a.state",
            "test_b.count",
            "test_c.time",
            "test_d.us_segment",
        ]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_complex_boolean_logic_members(self):
        payload = {
            "segments": [],
            "filters": [
                {
                    "or": [
                        {
                            "and": [
                                {
                                    "values": ["Corpus Christi"],
                                    "member": "test_a.city",
                                    "operator": "equals",
                                },
                                {
                                    "member": "test_b.age_bucket",
                                    "operator": "equals",
                                    "values": ["Senior adult"],
                                },
                            ]
                        },
                        {
                            "member": "test_c.city",
                            "operator": "equals",
                            "values": ["Sacramento"],
                        },
                    ]
                },
                {"or": [{"member": "test_d.city", "operator": "set"}]},
            ],
        }
        expected_members = [
            "test_a.city",
            "test_b.age_bucket",
            "test_c.city",
            "test_d.city",
        ]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_dimensions_only(self):
        payload = {"dimensions": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_members = ["test_a.city", "test_a.country", "test_a.state"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_measures_only(self):
        payload = {"measures": ["test_b.count"]}
        expected_members = ["test_b.count"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_filters_only(self):
        payload = {
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ]
        }
        expected_members = ["test_a.country"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_segments_only(self):
        payload = {"segments": ["test_a.us_segment"]}
        expected_members = ["test_a.us_segment"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_timeDimensions_only(self):
        payload = {
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ]
        }
        expected_members = ["test_c.time"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_empty_payload(self):
        payload = {}
        expected_members = []
        self.assertEqual(extract_members(payload), expected_members)

    def test_extract_members_with_invalid_keywords(self):
        payload = {"invalid": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_members = []
        self.assertEqual(extract_members(payload), expected_members)


if __name__ == "__main__":
    unittest.main()
