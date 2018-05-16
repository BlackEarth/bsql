
import os, subprocess, traceback, logging
from glob import glob
from bl.dict import Dict

from .model import Model

LOG = logging.getLogger(__name__)

class Migrate(Dict):
    def __init__(self, db, **Database):
        super().__init__(db=db, **Database)
    def __call__(self):
        Migration.migrate(self.db, migrations=self.migrations)

class Migration(Model):
    relation = 'migrations'
    pk = ['id']

    @classmethod
    def create_id(M, filename):
        return os.path.basename(os.path.splitext(filename)[0])

    @classmethod
    def migrate(M, db, migrations=None):
        """update the database with unapplied migrations"""
        migrations = migrations or db.migrations
        try:
            # will throw an error if this is the first migration -- migrations table doesn't yet exist.
            # (and this approach is a bit easier than querying for the existence of the table...)
            migrations_ids = [r.id for r in M(db).select()]
            LOG.debug("migrations_ids = " + str(migrations_ids))
        except:
            migrations_ids = []
        fns = [fn for fn 
                in glob(os.path.join(migrations, "[0-9]*-*.*"))     # active migrations have SEQ-NAME.*
                if M.create_id(fn) not in migrations_ids]
        fns.sort()
        LOG.info("Migrate Database: %d migrations in %r" % (len(fns), migrations))
        for fn in fns:
            id = M.create_id(fn)
            LOG.info(id + ': ' + fn)
            ext = os.path.splitext(fn)[1]
            if id in migrations_ids: 
                continue
            else:
                with open(fn, 'r') as f:
                    script = f.read()
                # description: first content line (after hash-bang and blank lines)
                lines = [l for l in script.split("\n") if l[:2]!='#!' and l.strip()!='']
                if len(lines) > 0:
                    description = lines[0].strip('-#/*; ')
                else:
                    description = ''
                LOG.info(id+ext + ': ' + description)
                
                if ext=='.sql':                                     # script is a SQL script, db.execute it
                    cursor = db.cursor()
                    db.execute(script, cursor=cursor)
                    cursor.connection.commit()
                    cursor.close()
                else:                                               # script is system script, subprocess it
                    LOG.info(subprocess.check_output([fn]))
                migration = M(db, id=id, description=description)
                migration.insert()
                
