
import re
from bl.text import Text


class SQL(Text):
    def __init__(self, comments=True, normalize=False, **args):
        super().__init__(**args)
        if self.text is not None and comments is False:
            # remove SQL comments
            self.text = re.sub(r'--.*?\n', '', self.text)
            if normalize is True:
                # convert all whitespace to single spaces
                self.text = re.sub(r'\s+', ' ', self.text)
                self.text = self.text.replace("( ", "(").replace(" )", ")")

    @classmethod
    def val(C, value):
        """return a string with a value ready for inclusion in SQL text."""
        if isinstance(value, str):
            return f"'{value}'"
        if value is None:
            return "null"
        elif value is True:
            return "true"
        elif value is False:
            return "false"
        else:
            return f"{value}"

    @classmethod
    def insert(C, record, keys=None, auto_pk=False):
        if keys is None:
            keys = [
                key
                for key in record.keys()
                if record[key] is not None and (auto_pk == False or key not in record.pk)
            ]
        return (
            f"INSERT INTO {record.relation} ({', '.join(keys)}) "
            + f"VALUES ({', '.join([C.val(record[key]) for key in keys])});"
        )
