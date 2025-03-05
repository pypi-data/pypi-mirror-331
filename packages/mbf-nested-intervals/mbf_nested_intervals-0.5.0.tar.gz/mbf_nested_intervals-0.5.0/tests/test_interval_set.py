from mbf_nested_intervals import IntervalSet


class TestIntervalSetCreation:
    def test_from_tuples(self):
        i = IntervalSet.from_tuples(
            [
                (1, 10),
                (1, 15),
                (0, 5),
            ]
        )
        assert i.to_tuples() == [
            (0, 5),
            (1, 15),
            (1, 10),
        ]
        assert len(i) == 3

    def test_from_tuples_with_id(self):
        i = IntervalSet.from_tuples_with_id(
            [
                (1, 10, 100),
                (1, 15, 200),
                (0, 5, 333),
            ]
        )
        assert i.to_tuples_first_id() == [
            (0, 5, 333),
            (1, 15, 200),
            (1, 10, 100),
        ]

    def test_from_tuples_with_id2(self):
        i = IntervalSet.from_tuples_with_id(
            [
                (1, 10, 100),
                (1, 15, 200),
                (0, 5, 333),
            ]
        )
        assert i.to_tuples_with_id() == [
            (0, 5, [333]),
            (1, 15, [200]),
            (1, 10, [100]),
        ]

    def test_invert(self):
        i = IntervalSet.from_tuples(
            [
                (5, 10),
            ]
        )
        i2 = i.invert(0, 15)
        assert i2.to_tuples() == [(0, 5), (10, 15)]

    def test_merge_hull(self):
        i = IntervalSet.from_tuples_with_id(
            [
                (1, 10, 100),
                (7, 15, 200),
                (0, 5, 333),
            ]
        )
        i2 = i.merge_hull()
        assert i2.to_tuples_with_id() == [(0, 15, [100, 200, 333])]

    def test_has_overlap_identical(self):
        i = IntervalSet.from_tuples_with_id(
            [
                (2, 10, 100),
                (20, 30, 200),
                (20, 30, 333),
                (40, 50, 333),
            ]
        )
        assert i.has_overlap(5, 6)
        assert i.has_overlap(22, 23)
        assert i.has_overlap(44, 45)
        assert not i.has_overlap(0, 1)
        assert not i.has_overlap(50, 60)
