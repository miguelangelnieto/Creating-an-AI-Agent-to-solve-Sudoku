assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

# Diagonals. A simple loop.
first_diagonal = [[rows[i]+cols[i] for i in range(9)]]
second_diagonal = [[rows[i]+cols[::-1][i] for i in range(9)]]

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Add the diagonals
unitlist = row_units + column_units + square_units + first_diagonal + second_diagonal
# Units. For each box, one unit for row, one for column and one for 3x3 square
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
# Peers. All the boxes on the same units (3 units as we see before)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

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

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    #print("Puzzle")
    #display(values)
    for box in boxes:
        # Only values with two items. Looks this is a constraint not really explained
        # in the lesson, but explained here:
        # https://discussions.udacity.com/t/looking-for-clarification-on-naked-twins-strategy/214011
        if len(values[box]) == 2:
            value = values[box]
            # Search for twins in the same unit
            for unit in units[box]:
                for unit_box in unit:
                    # If the value is the same and they are not the same box... we found a pair twin
                    if values[unit_box] == value and box != unit_box:
                        # We loop for each digit
                        for digit in list(value):
                            # Try to find the digit on the other boxes from same unit
                            for unit_box in unit:
                                if unit_box != box and values[unit_box] != value and len(values[unit_box])>=len(values[box]) and digit in values[unit_box]:
                                    final_digit = values[unit_box].replace(digit,'')
                                    values = assign_value(values, unit_box, final_digit)
    #print("\nSolution")
    #display(values)
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
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    pass

def eliminate(values):
    """
    If a box has a value already assigned, none of the
    can have the same value.
    Args:
        values(dict): The sudoky dictionary form
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            #values[peer] = values[peer].replace(digit,'')
            #assign_value(values, box, value)
            final_digit = values[peer].replace(digit,'')
            values = assign_value(values, peer, final_digit)
    return values

def only_choice(values):
    """
    If there is only one box in a unit which would 
    allow a certain digit, then that box must be 
    assigned that digit.
    Args:
        values(dict): The sudoky dictionary form
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #values[dplaces[0]] = digit
                #assign_value(values, box, value)
                values = assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Apply different techniques in order. There are checks to see if:
    - Sudoku is solved.
    - Sudoku is stalled.
    - There is no solution.
    Args:
        values(dict): The sudoky dictionary form
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Apply constraint propagation.
    Args:
        values(dict): The sudoky dictionary form
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
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