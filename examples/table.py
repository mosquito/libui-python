"""Example: Table with sample data."""

import libui
from libui import core


# Sample data
data = [
    ["Alice", "Engineer", 85],
    ["Bob", "Designer", 72],
    ["Carol", "Manager", 90],
    ["Dave", "Intern", 45],
    ["Eve", "Engineer", 95],
]


def num_columns():
    return 3


def column_type(col):
    if col < 2:
        return core.TableValueType.STRING
    return core.TableValueType.INT


def num_rows():
    return len(data)


def cell_value(row, col):
    val = data[row][col]
    if col == 2:
        return int(val)
    return str(val)


def set_cell_value(row, col, value):
    data[row][col] = value


async def main():
    w = core.Window("Table Example", 500, 300, False)

    model = core.TableModel(
        num_columns, column_type, num_rows, cell_value, set_cell_value
    )

    table = core.Table(model)
    table.append_text_column("Name", 0)
    table.append_text_column("Role", 1)
    table.append_progress_bar_column("Score", 2)

    def on_row_clicked(row):
        print(f"Clicked row {row}: {data[row][0]}")

    table.on_row_clicked(on_row_clicked)

    w.set_child(table)
    w.show()


if __name__ == "__main__":
    libui.run(main())
