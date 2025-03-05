from io import BytesIO
from json import dumps
from xlsxwriter import Workbook


def format_xlsx_sheet(
    json_sheet,
    worksheet,
    cell_format,
    MIN_COL_WIDTH=5,
    MAX_COL_WIDTH=100,
    FILTER_BUTTON_WIDTH=3,
):
    col_widths = [MIN_COL_WIDTH] * len(json_sheet["head"])
    for head_index, head in enumerate(json_sheet["head"]):
        col_widths[head_index] = max(col_widths[head_index], len(head))
    for row in json_sheet["body"]:
        for head_index, head in enumerate(json_sheet["head"]):
            if head in row:
                length = 0
                for string_part in row[head]:
                    length += len(string_part["text"])
                col_widths[head_index] = max(col_widths[head_index], length)
    for col_index, col_width in enumerate(col_widths):
        worksheet.set_column(
            first_col=col_index,
            last_col=col_index,
            width=min(MAX_COL_WIDTH, col_width + FILTER_BUTTON_WIDTH),
            cell_format=cell_format,
        )
    worksheet.freeze_panes(1, 0)
    if json_sheet["head"]:
        worksheet.autofilter(0, 0, len(json_sheet["body"]), len(json_sheet["head"]) - 1)


def write_formatted_xlsx_cells(
    json_sheet,
    workbook,
    worksheet,
):
    formats = {}
    for row_index, row in enumerate(json_sheet["body"]):
        for col_index, col in enumerate(json_sheet["head"]):
            if col in row:
                string_parts = []
                for string_part in row[col]:
                    if "format" in string_part:
                        format_json = dumps(obj=string_part["format"], sort_keys=True)
                        fmt = (
                            formats[format_json]
                            if format_json in formats
                            else workbook.add_format(string_part["format"])
                        )
                        formats[format_json] = fmt
                        string_parts.append(fmt)
                    string_parts.append(string_part["text"])
                if len(string_parts) == 1:
                    worksheet.write(row_index + 1, col_index, string_parts[0])
                elif len(string_parts) == 2:
                    worksheet.write(
                        row_index + 1, col_index, string_parts[1], string_parts[0]
                    )
                elif len(string_parts) >= 2:
                    worksheet.write_rich_string(row_index + 1, col_index, *string_parts)


def update_xlsx_workbook(data: list, workbook: Workbook) -> Workbook:
    """Take a json list of data sheets and an Excel Workbook, build the workbook contents from the data, and return the same workbook."""
    text_wrap_format = workbook.add_format()
    text_wrap_format.set_text_wrap()
    for json_sheet in data:
        worksheet = workbook.add_worksheet(json_sheet["title"])
        format_xlsx_sheet(json_sheet, worksheet, text_wrap_format)
        worksheet.write_row(0, 0, json_sheet["head"])
        write_formatted_xlsx_cells(json_sheet, workbook, worksheet)
    workbook.close()
    return workbook


def save_xlsx(data: list, filename: str) -> Workbook:
    """Take a json list of data sheets and filename, create an Excel file, and return the created workbook."""
    return update_xlsx_workbook(data, Workbook(filename))


def create_xlsx_stream(data: list) -> BytesIO:
    """Take a json list of data sheets, create an Excel workbook in memory, and return the created stream."""
    output = BytesIO()
    update_xlsx_workbook(data, Workbook(output, {"in_memory": True}))
    output.seek(0)
    return output