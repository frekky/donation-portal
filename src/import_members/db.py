"""
Route model operations to the correct database (when using more than one)
see https://docs.djangoproject.com/en/2.1/topics/db/multi-db/
"""

class MemberDbRouter:
    """
    Send all operations to the default database except for the old memberdb stuff (which goes to the memberdb_old database)
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'import_members':
            return 'memberdb_old'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'import_members':
            return 'memberdb_old'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Return the default setting
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure we don't do any migrations to the old database, it would only break things.
        """
        if app_label == 'import_members' or db == 'memberdb_old':
            return False
        return None
