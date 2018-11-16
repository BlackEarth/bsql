
import re, logging
from bl.text import Text
log = logging.getLogger(__name__)

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
            return f"""'{value.replace("'", "''")}'"""
        if value is None:
            return "NULL"
        elif value is True:
            return "TRUE"
        elif value is False:
            return "FALSE"
        else:
            return f"{value}"

    @classmethod
    def INSERT(C, record, keys=None, auto_pk=False, nulls=False, sp=' '):
        keys = [
            key
            for key in keys or record.keys()
            if (record[key] is not None or nulls == True)
            and (auto_pk == False or key not in record.pk)
        ]
        sql = (
            f"INSERT INTO {record.relation} ({(','+sp).join(keys)}) "
            + f"VALUES ({(','+sp).join([C.val(record[key]) for key in keys])});"
        )
        log.debug(sql)
        return sql

    @classmethod
    def UPDATE(C, record, keys=None, sp=' '):
        keys = [key for key in keys or record.keys() if key not in record.pk]
        sql = (
            f"UPDATE {record.relation} SET "
            + (","+sp).join([f"{key}={C.val(record[key])}" for key in keys])
            + " WHERE "
            + " AND ".join([f"{key}={C.val(record[key])}" for key in record.pk])
        )
        log.debug(sql)
        return sql
