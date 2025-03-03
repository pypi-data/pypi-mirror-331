import pytest

from textwrap import dedent
from pathlib import Path
import sys
import os

if __name__ == "__main__":  # to make the tests run without the pytest cli
    file_folder = Path(__file__).parent
    top_folder = (file_folder / ".." / "ndots").resolve()
    sys.path.insert(0, str(top_folder))
    os.chdir(file_folder)


from ndots import fiftydots
from ndots import fifteendots
from ndots import twentyfourdots
import ndots


def test_grid_non_proportional_0():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=False, width=None, align="c") == dedent(
        """\
<                                                                       >
<      *                     *          *        *       *     *    *** >
<      *                     *         * *       *             *   *   *>
< ***  * **   ***         ** *  ***    *    **** * **   **     *   *   *>
<    * **  * *           *  ** *   *  ***  *   * **  *   *     *   *****>
< **** *   * *           *   * *****   *   *   * *   *   *     *   *   *>
<*   * *   * *   *       *   * *       *   *  ** *   *   *         *   *>
< ****  ***   ***         ****  ***    *    ** * *   *  ***    *   *   *>
<                                              *                        >
<                                           ***                         >"""
    )


def test_grid_non_proportional_1():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=False, width=80, align="c") == dedent(
        """\
<                                                                                >
<          *                     *          *        *       *     *    ***      >
<          *                     *         * *       *             *   *   *     >
<     ***  * **   ***         ** *  ***    *    **** * **   **     *   *   *     >
<        * **  * *           *  ** *   *  ***  *   * **  *   *     *   *****     >
<     **** *   * *           *   * *****   *   *   * *   *   *     *   *   *     >
<    *   * *   * *   *       *   * *       *   *  ** *   *   *         *   *     >
<     ****  ***   ***         ****  ***    *    ** * *   *  ***    *   *   *     >
<                                                  *                             >
<                                               ***                              >"""
    )


def test_grid_non_proportional_2():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=False, width=80, align="c") == dedent(
        """\
<                                                                                >
<          *                     *          *        *       *     *    ***      >
<          *                     *         * *       *             *   *   *     >
<     ***  * **   ***         ** *  ***    *    **** * **   **     *   *   *     >
<        * **  * *           *  ** *   *  ***  *   * **  *   *     *   *****     >
<     **** *   * *           *   * *****   *   *   * *   *   *     *   *   *     >
<    *   * *   * *   *       *   * *       *   *  ** *   *   *         *   *     >
<     ****  ***   ***         ****  ***    *    ** * *   *  ***    *   *   *     >
<                                                  *                             >
<                                               ***                              >"""
    )


def test_grid_non_proportional_3():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=False, width=80, align="c") == dedent(
        """\
<                                                                                >
<          *                     *          *        *       *     *    ***      >
<          *                     *         * *       *             *   *   *     >
<     ***  * **   ***         ** *  ***    *    **** * **   **     *   *   *     >
<        * **  * *           *  ** *   *  ***  *   * **  *   *     *   *****     >
<     **** *   * *           *   * *****   *   *   * *   *   *     *   *   *     >
<    *   * *   * *   *       *   * *       *   *  ** *   *   *         *   *     >
<     ****  ***   ***         ****  ***    *    ** * *   *  ***    *   *   *     >
<                                                  *                             >
<                                               ***                              >"""
    )


def test_grid_non_proportional_4():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=False, width=40, align="c") == dedent(
        """\
<                                        >
<             *          *        *      >
<             *         * *       *      >
<*         ** *  ***    *    **** * **   >
<         *  ** *   *  ***  *   * **  *  >
<         *   * *****   *   *   * *   *  >
< *       *   * *       *   *  ** *   *  >
<*         ****  ***    *    ** * *   *  >
<                               *        >
<                            ***         >"""
    )


def test_grid_non_proportional_5():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=False, width=40, align="c") == dedent(
        """\
<                                        >
<             *          *        *      >
<             *         * *       *      >
<*         ** *  ***    *    **** * **   >
<         *  ** *   *  ***  *   * **  *  >
<         *   * *****   *   *   * *   *  >
< *       *   * *       *   *  ** *   *  >
<*         ****  ***    *    ** * *   *  >
<                               *        >
<                            ***         >"""
    )


def test_grid_non_proportional_6():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=False, width=40, align="c") == dedent(
        """\
<                                        >
<             *          *        *      >
<             *         * *       *      >
<*         ** *  ***    *    **** * **   >
<         *  ** *   *  ***  *   * **  *  >
<         *   * *****   *   *   * *   *  >
< *       *   * *       *   *  ** *   *  >
<*         ****  ***    *    ** * *   *  >
<                               *        >
<                            ***         >"""
    )


def test_grid_non_proportional_7():
    assert fiftydots.grid_to_str(s="", default=" ", intra=1, proportional=False, width=None, align="c") == dedent(
        """\
<>
<>
<>
<>
<>
<>
<>
<>
<>
<>"""
    )


def test_grid_non_proportional_8():
    assert fiftydots.grid_to_str(s=" ", default=" ", intra=1, proportional=False, width=None, align="c") == dedent(
        """\
<     >
<     >
<     >
<     >
<     >
<     >
<     >
<     >
<     >
<     >"""
    )


def test_grid_proportional_0():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=True, width=None, align="c") == dedent(
        """\
<                                                             >
<      *                  *         *        *      *  *  *** >
<      *                  *        * *       *         * *   *>
< ***  * **   ***      ** *  ***   *    **** * **  **  * *   *>
<    * **  * *        *  ** *   * ***  *   * **  *  *  * *****>
< **** *   * *        *   * *****  *   *   * *   *  *  * *   *>
<*   * *   * *   *    *   * *      *   *  ** *   *  *    *   *>
< ****  ***   ***      ****  ***   *    ** * *   * *** * *   *>
<                                          *                  >
<                                       ***                   >"""
    )


def test_grid_proportional_1():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=True, width=80, align="c") == dedent(
        """\
<                                                                                >
<               *                  *         *        *      *  *  ***           >
<               *                  *        * *       *         * *   *          >
<          ***  * **   ***      ** *  ***   *    **** * **  **  * *   *          >
<             * **  * *        *  ** *   * ***  *   * **  *  *  * *****          >
<          **** *   * *        *   * *****  *   *   * *   *  *  * *   *          >
<         *   * *   * *   *    *   * *      *   *  ** *   *  *    *   *          >
<          ****  ***   ***      ****  ***   *    ** * *   * *** * *   *          >
<                                                   *                            >
<                                                ***                             >"""
    )


def test_grid_proportional_2():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=True, width=80, align="c") == dedent(
        """\
<                                                                                >
<               *                  *         *        *      *  *  ***           >
<               *                  *        * *       *         * *   *          >
<          ***  * **   ***      ** *  ***   *    **** * **  **  * *   *          >
<             * **  * *        *  ** *   * ***  *   * **  *  *  * *****          >
<          **** *   * *        *   * *****  *   *   * *   *  *  * *   *          >
<         *   * *   * *   *    *   * *      *   *  ** *   *  *    *   *          >
<          ****  ***   ***      ****  ***   *    ** * *   * *** * *   *          >
<                                                   *                            >
<                                                ***                             >"""
    )


def test_grid_proportional_3():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=True, width=80, align="c") == dedent(
        """\
<                                                                                >
<               *                  *         *        *      *  *  ***           >
<               *                  *        * *       *         * *   *          >
<          ***  * **   ***      ** *  ***   *    **** * **  **  * *   *          >
<             * **  * *        *  ** *   * ***  *   * **  *  *  * *****          >
<          **** *   * *        *   * *****  *   *   * *   *  *  * *   *          >
<         *   * *   * *   *    *   * *      *   *  ** *   *  *    *   *          >
<          ****  ***   ***      ****  ***   *    ** * *   * *** * *   *          >
<                                                   *                            >
<                                                ***                             >"""
    )


def test_grid_proportional_4():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=True, width=40, align="c") == dedent(
        """\
<                                        >
<               *         *        *     >
<               *        * *       *     >
<   ***      ** *  ***   *    **** * **  >
<* *        *  ** *   * ***  *   * **  * >
<* *        *   * *****  *   *   * *   * >
<* *   *    *   * *      *   *  ** *   * >
<   ***      ****  ***   *    ** * *   * >
<                                *       >
<                             ***        >"""
    )


def test_grid_proportional_5():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=True, width=40, align="c") == dedent(
        """\
<                                        >
<               *         *        *     >
<               *        * *       *     >
<   ***      ** *  ***   *    **** * **  >
<* *        *  ** *   * ***  *   * **  * >
<* *        *   * *****  *   *   * *   * >
<* *   *    *   * *      *   *  ** *   * >
<   ***      ****  ***   *    ** * *   * >
<                                *       >
<                             ***        >"""
    )


def test_grid_proportional_6():
    assert fiftydots.grid_to_str(s="abc defghi!A", default=" ", intra=1, proportional=True, width=40, align="c") == dedent(
        """\
<                                        >
<               *         *        *     >
<               *        * *       *     >
<   ***      ** *  ***   *    **** * **  >
<* *        *  ** *   * ***  *   * **  * >
<* *        *   * *****  *   *   * *   * >
<* *   *    *   * *      *   *  ** *   * >
<   ***      ****  ***   *    ** * *   * >
<                                *       >
<                             ***        >"""
    )


def test_grid_proportional_7():
    assert fiftydots.grid_to_str(s="", default=" ", intra=1, proportional=True, width=None, align="c") == dedent(
        """\
<>
<>
<>
<>
<>
<>
<>
<>
<>
<>"""
    )


def test_grid_proportional_8():
    assert fiftydots.grid_to_str(s=" ", default=" ", intra=1, proportional=True, width=None, align="c") == dedent(
        """\
<  >
<  >
<  >
<  >
<  >
<  >
<  >
<  >
<  >
<  >"""
    )


def test_grid_twentyfourdots():

    assert twentyfourdots.grid_to_str("mwGMW", intra=2, proportional=True, width=None, align="c") == dedent(
        """\
<           *   * *  * *>
<          * *  ***  * *>
<* *  * *  *    ***  * *>
<***  * *  * *  * *  * *>
<* *  * *  * *  * *  ***>
<* *  ***  * *  * *  ***>
<* *  * *   *   * *  * *>
<                       >"""
    )
    assert twentyfourdots.number_of_pixels("mwGMW", intra=2, proportional=True) == 23


def test_misc():
    assert fifteendots.width() == 3
    assert fifteendots.height() == 5
    assert fifteendots.has_char("a")

    assert fiftydots.width() == 5
    assert fiftydots.height() == 10
    assert fiftydots.has_char("a")

    assert twentyfourdots.width() == 3
    assert twentyfourdots.height() == 8
    assert twentyfourdots.has_char("a")

    assert set(ndots.available_fonts()) == {fifteendots, fiftydots, twentyfourdots}


if __name__ == "__main__":
    pytest.main(["-vv", "-s", "-x", __file__])
