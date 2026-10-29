import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from hardcoded_path_finder.cli import main
from hardcoded_path_finder.core import scan_text


def kinds(text, **kw):
    return [(h.kind, h.path) for h in scan_text(text, **kw)]


class ScanTests(unittest.TestCase):
    def test_windows_and_unix_paths(self):
        src = 'df = read_csv("C:\\\\Users\\\\ana\\\\data.csv")\nx = open("/home/bob/project/raw.txt")\n'
        k = kinds(src)
        self.assertEqual(k[0][0], "windows-drive")
        self.assertIn("data.csv", k[0][1])
        self.assertEqual(k[1], ("unix-home", "/home/bob/project/raw.txt"))

    def test_mac_tilde_volume_cloud(self):
        src = "a = '/Users/ana/Desktop/x.csv'\nb = '~/data/y.csv'\nc = '/Volumes/LabDrive/run1'\nd = 'D:/OneDrive - Uni/z.xlsx'\n"
        found = [k for k, _ in kinds(src)]
        self.assertEqual(found[:3], ["unix-home", "tilde-home", "mounted-volume"])
        self.assertIn("windows-drive", found)

    def test_urls_relative_and_comments_ignored(self):
        src = ('url = "https://example.org/home/user/data"\np = "data/raw.csv"\n'
               '# see /home/bob/notes\nq = Path(__file__).parent / "data"\n')
        self.assertEqual(kinds(src), [])

    def test_line_and_column(self):
        h = scan_text('x = 1\ny = "/home/u/f.txt"\n')[0]
        self.assertEqual((h.line, h.col), (2, 6))

    def test_non_string_mode_for_configs(self):
        self.assertEqual(kinds("data_dir = /home/lab/data\n", strings_only=False)[0][0], "unix-home")

    def test_cli_scans_notebooks_and_configs(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.ipynb"), "w", encoding="utf-8") as fh:
                json.dump({"cells": [{"cell_type": "code", "source": ["pd.read_csv('/Users/me/x.csv')"]}]}, fh)
            with open(os.path.join(d, "config.yaml"), "w", encoding="utf-8") as fh:
                fh.write("out: E:\\results\\run1\n")
            with redirect_stdout(io.StringIO()) as buf:
                self.assertEqual(main([d]), 1)
            self.assertIn("2 file(s) scanned, 2 hard-coded path(s)", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
