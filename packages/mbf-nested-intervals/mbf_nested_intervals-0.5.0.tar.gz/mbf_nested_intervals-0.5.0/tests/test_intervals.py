import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from mbf_nested_intervals import merge_df_intervals, merge_df_intervals_with_callback


class TestIntervals:
    def test_merge_intervals(self):
        df = pd.DataFrame(
            [
                {"chr": "1", "start": 0, "stop": 1000, "key": "a"},
                {"chr": "1", "start": 850, "stop": 860, "key": "b"},
                {"chr": "1", "start": 900, "stop": 1100, "key": "c"},
                {"chr": "2", "start": 900, "stop": 1100, "key": "d"},
            ]
        )
        merged = merge_df_intervals(df)
        should = pd.DataFrame(
            [
                {"index": 2, "chr": "1", "start": 0, "stop": 1100, "key": "c"},
                {"index": 3, "chr": "2", "start": 900, "stop": 1100, "key": "d"},
            ]
        ).set_index("index")
        should.index.name = None
        assert_frame_equal(merged, should)

    def test_merge_intervals2(self):

        import traceback
        import warnings
        import sys

        def warn_with_traceback(message, category, filename, lineno, file=None, line=None):

            log = file if hasattr(file,'write') else sys.stderr
            traceback.print_stack(file=log)
            log.write(warnings.formatwarning(message, category, filename, lineno, line))

        warnings.showwarning = warn_with_traceback

        df = pd.DataFrame(
            [
                {"chr": "Chromosome", "start": 10, "stop": 100},
                {"chr": "Chromosome", "start": 400, "stop": 450},
                {"chr": "Chromosome", "start": 80, "stop": 120},
                {"chr": "Chromosome", "start": 600, "stop": 700},
            ]
        )
        merged = merge_df_intervals(df)
        should = pd.DataFrame(
            [
                {"index": 2, "chr": "Chromosome", "start": 10, "stop": 120},
                {"index": 1, "chr": "Chromosome", "start": 400, "stop": 450},
                {"index": 3, "chr": "Chromosome", "start": 600, "stop": 700},
            ]
        ).set_index("index")
        should.index.name = None
        assert_frame_equal(merged, should)

    def test_merge_intervals_with_strand(self):

        import traceback
        import warnings
        import sys

        def warn_with_traceback(message, category, filename, lineno, file=None, line=None):

            log = file if hasattr(file,'write') else sys.stderr
            traceback.print_stack(file=log)
            log.write(warnings.formatwarning(message, category, filename, lineno, line))

        warnings.showwarning = warn_with_traceback

        df = pd.DataFrame(
            [
                {"chr": "Chromosome", "start": 10, "stop": 100, 'strand': 1},
                {"chr": "Chromosome", "start": 400, "stop": 450, 'strand': 1},
                {"chr": "Chromosome", "start": 80, "stop": 120, 'strand': -1},
                {"chr": "Chromosome", "start": 600, "stop": 700, 'strand': 1},
                {"chr": "Chromosome", "start": 100, "stop": 140, 'strand': -1},
            ]
        )
        merged = merge_df_intervals(df)
        should = pd.DataFrame(
            [
                {"index": 0, "chr": "Chromosome", "start": 10, "stop": 100, 'strand': 1},
                {"index": 4, "chr": "Chromosome", "start": 80, "stop": 140, 'strand': -1},
                {"index": 1, "chr": "Chromosome", "start": 400, "stop": 450, 'strand': 1},
                {"index": 3, "chr": "Chromosome", "start": 600, "stop": 700, 'strand': 1},
            ]
        ).set_index("index")
        should.index.name = None
        print(merged)
        assert_frame_equal(merged, should)

    def test_merge_df_intervals_with_callback(self):
        df = pd.DataFrame(
            [
                {"chr": "1", "start": 0, "stop": 1000, "key": "a"},
                {"chr": "1", "start": 850, "stop": 860, "key": "b"},
                {"chr": "1", "start": 900, "stop": 1100, "key": "c"},
                {"chr": "2", "start": 900, "stop": 1100, "key": "d"},
            ]
        )

        def cb(sub_df):
            res = sub_df.iloc[0].to_dict()
            res["key"] = "".join(sub_df["key"])
            return res

        merged = merge_df_intervals_with_callback(df, cb)

        should = pd.DataFrame(
            [
                {"chr": "1", "start": 0, "stop": 1100, "key": "abc"},
                {"chr": "2", "start": 900, "stop": 1100, "key": "d"},
            ]
        )
        assert_frame_equal(merged, should)

    def test_merge_df_intervals_with_callback(self):
        df = pd.DataFrame(
            [
                {"chr": "1", "start": 0, "stop": 1000, "key": "a"},
                {"chr": "1", "start": 850, "stop": 860, "key": "b"},
                {"chr": "1", "start": 900, "stop": 1100, "key": "c"},
                {"chr": "2", "start": 900, "stop": 1100, "key": "d"},
            ]
        )

        def cb(sub_df):
            res = sub_df.iloc[0]
            return res

        with pytest.raises(ValueError):
            merge_df_intervals_with_callback(df, cb)

    def test_merge_df_intervals_with_callback(self):
        df = pd.DataFrame(
            [
                {"chr": "1", "start": 0, "stop": 1000, "key": "a"},
                {"chr": "1", "start": 850, "stop": 860, "key": "b"},
                {"chr": "1", "start": 900, "stop": 1100, "key": "c"},
                {"chr": "2", "start": 900, "stop": 1100, "key": "d"},
            ]
        )

        def cb(sub_df):
            res = sub_df.iloc[0].to_dict()
            del res["key"]
            return res

        with pytest.raises(ValueError):
            merge_df_intervals_with_callback(df, cb)

    def test_merge_df_intervals_with_callback(self):
        df = pd.DataFrame(
            [
                {"chr": "1", "start": 0, "stop": 1000, "key": "a"},
                {"chr": "1", "start": 850, "stop": 860, "key": "b"},
                {"chr": "1", "start": 900, "stop": 1100, "key": "c"},
                {"chr": "2", "start": 900, "stop": 1100, "key": "d"},
            ]
        )

        def cb(sub_df):
            res = sub_df.iloc[0].to_dict()
            res["key_merged"] = "".join(sub_df["key"])
            return res

        with pytest.raises(ValueError):
            merge_df_intervals_with_callback(df, cb)
