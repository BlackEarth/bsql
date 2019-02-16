import os, subprocess, traceback, logging
from glob import glob
from bl.dict import Dict

from .model import Model

LOG = logging.getLogger(__name__)


class Migration(Model):
    relation = 'migrations'
    pk = ['id']

    @classmethod
    def get_id(M, filename):
        return os.path.basename(os.path.splitext(filename)[0])

    @classmethod
    def migrate(M, db, migrations=None):
        """update the database with unapplied migrations"""
        migrations = migrations or db.migrations
        try:
            # throws an error if migrations table doesn't yet exist.
            migration_ids = [r.id for r in M(db).select()]
            LOG.debug("migration_ids = " + str(migration_ids))
        except:
            migration_ids = []
        # active migrations have SEQ-NAME.*
        fns = [
            fn
            for fn in glob(os.path.join(migrations, "[0-9]*-*.*"))
            if M.get_id(fn) not in migration_ids
        ]
        fns.sort()
        LOG.info("Migrate Database: %d migrations in %r" % (len(fns), migrations))
        for fn in fns:
            id = M.get_id(fn)
            # LOG.info(id + ': ' + fn)
            ext = os.path.splitext(fn)[1]
            if id in migration_ids:
                continue
            else:
                with open(fn, 'r') as f:
                    script = f.read()
                # description: first content line (after hash-bang and blank lines)
                lines = [l for l in script.split("\n") if l[:2] != '#!' and l.strip() != '']
                if len(lines) > 0:
                    description = lines[0].strip('-#/*; ')
                else:
                    description = ''

                cursor = db.cursor()
                if ext == '.sql':  # script is a SQL script, db.execute it
                    db.execute(script, cursor=cursor)
                elif ext == '.py':  # script is a python script
                    subprocess.check_output(['python', fn])
                else:  # script is system script, subprocess it
                    subprocess.check_output([fn])
                migration = M(db, id=id, description=description)
                migration.insert(cursor=cursor)
                cursor.connection.commit()
                cursor.close()
                print(f"[{migration.inserted}] {migration.id}: {migration.description}")
