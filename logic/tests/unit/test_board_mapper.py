from controller.board_mapper import BoardMapper


def test_top_left_cell():
    m = BoardMapper(cell_size=100)
    assert m.to_cell(0, 0) == (0, 0)


def test_pixel_within_first_cell():
    m = BoardMapper(cell_size=100)
    assert m.to_cell(99, 99) == (0, 0)


def test_second_column():
    m = BoardMapper(cell_size=100)
    assert m.to_cell(100, 0) == (0, 1)


def test_second_row():
    m = BoardMapper(cell_size=100)
    assert m.to_cell(0, 100) == (1, 0)


def test_arbitrary_cell():
    m = BoardMapper(cell_size=100)
    assert m.to_cell(350, 250) == (2, 3)


def test_custom_cell_size():
    m = BoardMapper(cell_size=64)
    assert m.to_cell(128, 64) == (1, 2)
