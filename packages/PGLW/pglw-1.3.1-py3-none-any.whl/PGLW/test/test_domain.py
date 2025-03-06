import unittest

import numpy as np

from PGLW.main.domain import Block, Domain, read_x3dunf, write_x3dunf


# todo: many more test cases needed, this is a start
def make_domain(nb):
    d = Domain()
    for n in range(nb):
        x = np.ones((17, 17, 17))
        y = np.ones((17, 17, 17)) * 2.0
        z = np.ones((17, 17, 17)) * 4.0
        attr = np.ones((17, 17, 17), dtype=int) * 101
        d.add_blocks(Block(x, y, z, attr=attr))
    return d


class TestDomain(unittest.TestCase):
    def test_read_write_x3dunf(self):
        d = make_domain(4)
        write_x3dunf(d, "test.x3dunf", add_ghosts=True)

        dd = read_x3dunf("test.x3dunf", include_ghost=False)

        assert np.mean(dd.blocks["block-0000"].x) == 1.0
        assert np.mean(dd.blocks["block-0000"].y) == 2.0
        assert np.mean(dd.blocks["block-0000"].z) == 4.0
        assert np.mean(dd.blocks["block-0000"].scalars["attr"]) == 101

    def test_split_blocks(self):
        d = make_domain(1)
        d.blocks["block-0000"].scalars["attr"][:9, :9, :9] = 200
        d.split_blocks(9)
        self.assertTrue(
            np.all(d.blocks["block-split0000"].scalars["attr"] == 200)
        )


if __name__ == "__main__":
    unittest.main()
    # d = make_domain(1)
    # d.blocks['block-0000'].scalars['attr'][:9, :9, :9] = 200
    # d.split_blocks(bsize=9)
