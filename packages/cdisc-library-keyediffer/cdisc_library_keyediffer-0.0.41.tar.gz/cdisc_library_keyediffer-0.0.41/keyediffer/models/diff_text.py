from difflib import SequenceMatcher


class DiffText:
    """Represents a diff between a pair of text"""

    FORMATS = {
        "REPLACE_FORMAT": {"bold": True, "color": "#FF3300"},  # Orange-Red
        "BORDER_FORMAT": {"bold": True, "color": "#00CC55"},  # Blue-Green
    }

    FORMAT = "format"
    MARKER = "marker"
    TEXT = "text"

    OPCODE_CASES = {
        "equal": "_opcode_equal",
        "replace": "_opcode_replace",
        "delete": "_opcode_delete",
        "insert": "_opcode_insert",
    }

    def __init__(
        self,
        old: any = None,
        new: any = None,
    ):
        # Value update - Determine string indices for highlighting differences
        opcodes = SequenceMatcher(
            None,
            old,
            new,
            False,
        ).get_opcodes()
        self.opcodes = opcodes
        self.old_val = []
        self.new_val = []
        # These 2 variables are lists of dicts and markers.
        # dict - Each dict contains a chunk of text and, if it is not plaintext, a format that applies to that chunk of text.
        # marker - This is a string that represents a location where text was removed or dropped in the diff pair.
        self.old_str = []
        self.new_str = []
        for opcode in opcodes:
            getattr(self, DiffText.OPCODE_CASES[opcode[0]])(
                old[opcode[1] : opcode[2]],
                new[opcode[3] : opcode[4]],
            )
        DiffText._highlight_surrounding(self.old_str)
        DiffText._highlight_surrounding(self.new_str)
        self.old_str = DiffText._combine_adjacent_same_format(self.old_str)
        self.new_str = DiffText._combine_adjacent_same_format(self.new_str)

    def _opcode_equal(
        self,
        old_substr: str,
        new_substr: str,
    ):
        self.old_str.append({DiffText.TEXT: old_substr})
        self.new_str.append({DiffText.TEXT: new_substr})

    def _opcode_replace(
        self,
        old_substr: str,
        new_substr: str,
    ):
        self.old_str.append(
            {
                DiffText.TEXT: old_substr,
                DiffText.FORMAT: DiffText.FORMATS["REPLACE_FORMAT"],
            }
        )
        self.new_str.append(
            {
                DiffText.TEXT: new_substr,
                DiffText.FORMAT: DiffText.FORMATS["REPLACE_FORMAT"],
            }
        )
        self.old_val.append(old_substr)
        self.new_val.append(new_substr)

    def _opcode_delete(
        self,
        old_substr: str,
        new_substr: str,
    ):
        self.old_str.append(
            {
                DiffText.TEXT: old_substr,
                DiffText.FORMAT: DiffText.FORMATS["REPLACE_FORMAT"],
            }
        )
        self.new_str.append(DiffText.MARKER)
        if new_substr:
            self.new_str.append(
                {
                    DiffText.TEXT: new_substr,
                }
            )
        self.old_val.append(old_substr)
        self.new_val.append(new_substr)

    def _opcode_insert(
        self,
        old_substr: str,
        new_substr: str,
    ):
        self.old_str.append(DiffText.MARKER)
        if old_substr:
            self.old_str.append(
                {
                    DiffText.TEXT: old_substr,
                }
            )
        self.new_str.append(
            {
                DiffText.TEXT: new_substr,
                DiffText.FORMAT: DiffText.FORMATS["REPLACE_FORMAT"],
            }
        )
        self.old_val.append(old_substr)
        self.new_val.append(new_substr)

    @staticmethod
    def _highlight_single_char(
        texts: list, relative_marker_index: int, string: str, non_space_index: int
    ):
        replacements = []
        if non_space_index > 0:
            replacements.append({DiffText.TEXT: string[:non_space_index]})
        replacements.append(
            {
                DiffText.FORMAT: DiffText.FORMATS["BORDER_FORMAT"],
                DiffText.TEXT: string[non_space_index : non_space_index + 1],
            }
        )
        if non_space_index < len(string) - 1:
            replacements.append({DiffText.TEXT: string[non_space_index + 1 :]})
        texts[relative_marker_index : relative_marker_index + 1] = replacements

    @staticmethod
    def _highlight_surrounding(texts: list):
        marker_index = texts.index(DiffText.MARKER) if DiffText.MARKER in texts else -1
        while marker_index >= 0:
            # Highlight "after" index first, so that we don't mess up the index when we go to highlight "before" index
            relative_marker_index = marker_index + 1
            while (
                relative_marker_index < len(texts)
                and texts[relative_marker_index] != DiffText.MARKER
            ):
                text = texts[relative_marker_index]
                string = text[DiffText.TEXT]
                if not string.isspace():
                    if DiffText.FORMAT not in text:
                        # Replace the proceeding text with a highlighted string
                        DiffText._highlight_single_char(
                            texts,
                            relative_marker_index,
                            string,
                            len(string) - len(string.lstrip()),
                        )
                    break
                relative_marker_index += 1
            # Highlight "before" index
            relative_marker_index = marker_index - 1
            while (
                relative_marker_index >= 0
                and texts[relative_marker_index] != DiffText.MARKER
            ):
                text = texts[relative_marker_index]
                string = text[DiffText.TEXT]
                if not string.isspace():
                    if DiffText.FORMAT not in text:
                        # Replace the preceeding text with a highlighted string
                        DiffText._highlight_single_char(
                            texts,
                            relative_marker_index,
                            string,
                            len(string.rstrip()) - 1,
                        )
                    break
                relative_marker_index -= 1
            # Prepare for next iteration
            texts.remove(DiffText.MARKER)
            marker_index = (
                texts.index(DiffText.MARKER) if DiffText.MARKER in texts else -1
            )

    @staticmethod
    def _combine_adjacent_same_format(texts: list) -> list:
        """
        Take a list of formatted text chunks. If two adjacent text chunks have the same format, concatenate the text chunks together into a single chunk with the same format.
        Returns the combined list. len(combined) <= len(texts)

        Keyword arguments:
        texts -- List of dicts. Each dict contains a chunk of text and, if it is not plaintext, a format that applies to that chunk of text.
        """
        combined = []
        for text_index, text in enumerate(texts):
            if text_index == 0 or text.get(DiffText.FORMAT, None) != texts[
                text_index - 1
            ].get(DiffText.FORMAT, None):
                combined.append(text)
            else:
                combined[-1][DiffText.TEXT] += text[DiffText.TEXT]
        return combined
