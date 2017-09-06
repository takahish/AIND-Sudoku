import re

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]


# Global Constants
_ROWS = 'ABCDEFGHI'
_COLS = '123456789'
_IS_DIAGONAL = True


# Global Variables
_boxes = cross(_ROWS, _COLS)

_row_units = [cross(r, _COLS) for r in _ROWS]
_column_units = [cross(_ROWS, c) for c in _COLS]
_square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
_diagonal_units = [[s+t for s, t in zip(_ROWS, _COLS)], [s+t for s, t in zip(_ROWS, _COLS[::-1])]]

_unitlist = _row_units + _column_units + _square_units
if _IS_DIAGONAL:
    _unitlist = _unitlist + _diagonal_units

_units = dict((s, [u for u in _unitlist if s in u]) for s in _boxes)

_peers = dict((s, set(sum(_units[s], [])) - set([s])) for s in _boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in _unitlist:
        # Find all instances of naked twins
        ## First, find boxes that have two possibilities
        twins_boxes = [box for box in unit if len(values[box]) == 2]
        ## Next, find box pairs have the naked twins
        naked_twins = {}
        for i, ibox in enumerate(twins_boxes[:-1]):
            for _, jbox in enumerate(twins_boxes[i+1:]):
                if values[ibox] == values[jbox]:
                    naked_twins[values[ibox]] = (ibox, jbox)

        # Eliminate the naked twins as possibilities for their peers
        for twins, pair in naked_twins.items():
            for peer in [box for box in unit if box not in pair]:
                values = assign_value(values, peer, re.sub('['+twins+']', '', values[peer]))

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.

    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(_boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.

    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in _boxes)
    line = '+'.join(['_'*(width*3)]*3)
    for r in _ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in _COLS))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value,
    eliminate this value from the values of all its peers.

    Args:
        A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in _peers[box]:
            values = assign_value(values, peer, values[peer].replace(digit, ''))
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    for unit in _unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box
    with no available values, return False. If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.

    Args:
        A sudoku in dictionary form.
    Retruns:
        The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = naked_twins(values) # naked_twins
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, try all possible values.

    Args:
        A sudoku in dictionary form.
    Retruns:
        The resulting sudoku in dictionary form.
    """
    values = reduce_puzzle(values)

    # Termination
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in _boxes):
        return values ## Solved!

    # Recursion
    n, s = min((len(values[s]), s) for s in _boxes if len(values[s]) > 1)
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.

    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
