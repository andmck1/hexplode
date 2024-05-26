from game import Hexplode
import logging
from typing import List, Tuple


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


test_data = [
    (2, (0, 0, 0), (0, 0), (1, 2)),
    (2, (0, -1, 1), (1, 1), (0, 3)),
    (2, (1, -1, 0), (2, 0), (1, 4)),
    (2, (1, 0, -1), (1, -1), (2, 3)),
    (2, (0, 1, -1), (-1, -1), (2, 1)),
    (2, (-1, 1, 0), (-2, 0), (1, 0)),
    (2, (-1, 0, 1), (-1, 1), (0, 1)),
    (3, (0, 0, 0), (0, 0), (2, 4)),
    (3, (-1, 0, 1), (-1, 1), (1, 3)),
    (3, (0, -1, 1), (1, 1), (1, 5)),
    (3, (1, -1, 0), (2, 0), (2, 6)),
    (3, (1, 0, -1), (1, -1), (3, 5)),
    (3, (0, 1, -1), (-1, -1), (3, 3)),
    (3, (-1, 1, 0), (-2, 0), (2, 2)),
    (3, (-1, 0, 1), (-1, 1), (1, 3)),
    (3, (-1, -1, 2), (0, 2), (0, 4)),
    (3, (0, -2, 2), (2, 2), (0, 6)),
    (3, (1, -2, 1), (3, 1), (1, 7)),
    (3, (2, -2, 0), (4, 0), (2, 8)),
    (3, (2, -1, -1), (3, -1), (3, 7)),
    (3, (2, 0, -2), (2, -2), (4, 6)),
    (3, (1, 1, -2), (0, -2), (4, 4)),
    (3, (0, 2, -2), (-2, -2), (4, 2)),
    (3, (-1, 2, -1), (-3, -1), (3, 1)),
    (3, (-2, 2, 0), (-4, 0), (2, 0)),
    (3, (-2, 1, 1), (-3, 1), (1, 1)),
    (3, (-2, 0, 2), (-2, 2), (0, 2)),
]


def get_hex_coords(dim: int) -> List[Tuple]:
    hex_coords_1d = [
        (0, 0, 0),
    ]
    hex_coords_2d = [
        *hex_coords_1d,
        (0, -1, 1),
        (1, -1, 0),
        (1, 0, -1),
        (0, 1, -1),
        (-1, 1, 0),
        (-1, 0, 1),
    ]
    hex_coords_3d = [
        *hex_coords_2d,
        (-1, -1, 2),
        (0, -2, 2),
        (1, -2, 1),
        (2, -2, 0),
        (2, -1, -1),
        (2, 0, -2),
        (1, 1, -2),
        (0, 2, -2),
        (-1, 2, -1),
        (-2, 2, 0),
        (-2, 1, 1),
        (-2, 0, 2),
    ]
    match dim:
        case 1:
            return hex_coords_1d
        case 2:
            return hex_coords_2d
        case 3:
            return hex_coords_3d
        case _:
            return list(tuple())


def test_hexagonal_coordinates():
    for size in range(1, 4):
        hexplode = Hexplode(size=size)
        hex_coords = sorted(list(hexplode.hexagonal_coordinates(size)))
        expected_hex_coords = sorted(list(get_hex_coords(size)))
        logger.info(f"testing with size={size}")
        if size == 3:
            print(hex_coords)
            print(expected_hex_coords)
        assert hex_coords == expected_hex_coords


def test_hexagonal_neigbours():
    size = 3
    hexplode = Hexplode(size=size)
    test_neighbour_data = [
        (
            (0, 0, 0),
            [
                (0, -1, 1),
                (1, -1, 0),
                (1, 0, -1),
                (0, 1, -1),
                (-1, 1, 0),
                (-1, 0, 1),
            ],
        ),
        ((-2, 0, 2), [(-1, -1, 2), (-1, 0, 1), (-2, 1, 1)]),
    ]
    for node, expected_neighbours in test_neighbour_data:
        neighbours = hexplode.hexagonal_neighbours(*node, size=size)
        assert sorted(expected_neighbours) == sorted(neighbours)


def test_cubic_to_pixel():
    for _, cubic_node, expected_pixel_node, _ in test_data:
        pixel_node = Hexplode.cubic_to_pixel(*cubic_node)
        assert pixel_node == expected_pixel_node


def test_pixel_to_array():
    for size, _, pixel_node, expected_array_coords in test_data:
        array_coords = Hexplode.pixel_to_array(*pixel_node, n=size)
        assert array_coords == expected_array_coords


def test_create_hexagonal_board():
    pass


def test_initialise_board_graph():
    pass


def test_create_board():
    hexplode = Hexplode(size=2)
    expected_board = (
        "|.|0|.|0|.|\n"  # fmt: skip
        "|0|.|0|.|0|\n"  # fmt: skip
        "|.|0|.|0|.|\n"  # fmt: skip
    )
    board = hexplode.create_board()

    hexplode = Hexplode(size=3)
    expected_board = (
        "|.|.|0|.|0|.|0|.|.|\n"  # fmt: skip
        "|.|0|.|0|.|0|.|0|.|\n"  # fmt: skip
        "|0|.|0|.|0|.|0|.|0|\n"  # fmt: skip
        "|.|0|.|0|.|0|.|0|.|\n"  # fmt: skip
        "|.|.|0|.|0|.|0|.|.|\n"  # fmt: skip
    )
    board = hexplode.create_board()
    assert board == expected_board
