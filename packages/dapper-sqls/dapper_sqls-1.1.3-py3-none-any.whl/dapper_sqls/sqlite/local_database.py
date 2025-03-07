# coding: utf-8
from sqlalchemy import create_engine, text, insert, delete, update
from .models import BaseTables, Path, System, EnvVar
from .utils import get_value

class BaseLocalDatabase(object):

    def __init__(self, app_name : str, path : str, is_new_database : bool):
        self._app_name = app_name
        self.is_new_database = is_new_database
        self._engine = create_engine(f'sqlite:///{path}')
        
    @property
    def engine(self):
        return self._engine

    @property
    def app_name(self):
        return self._app_name
 
    def select(self, table : str, where : str = None):
        with self.engine.connect() as conn:
            if where:
                query = conn.execute(text(f"select * from {table} where App = '{self.app_name}' and {where}"))
            else:
                query = conn.execute(text(f"select * from {table} where App = '{self.app_name}'"))
            data = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
            return data

    def get_path(self, name):
        name = get_value(name)
        data = self.select('path', f"Name = '{name}'")
        for d in data:
            return Path(d).Path

    def update_path(self, name : str, path_name : str):
        name = get_value(name)
        path_name = get_value(path_name)
        existsPath = self.get_path(name)

        with self.engine.connect() as conn:
            if existsPath != None:
                stmt = update(BaseTables.path).where(
                    (BaseTables.path.c.Name == name) &
                    (BaseTables.path.c.App == self.app_name)
                ).values(Path=path_name)
                conn.execute(stmt)
            else:
                ins = insert(BaseTables.path).values(App=self.app_name, Name=name, Path=path_name)
                conn.execute(ins)
            conn.commit()

    def delete_path(self, name : str):
        name = get_value(name)
        with self.engine.connect() as conn:
            stmt = delete(BaseTables.path).where((BaseTables.path.c.Name == name) & (BaseTables.env_var.c.App == self.app_name))
            conn.execute(stmt)
            conn.commit()

    def get_var(self, name):
        name = get_value(name)
        data = self.select('env_var', f"name = '{name}'")
        for d in data:
            return EnvVar(d).Value

    def update_var(self, name : str, value : str):
        name = get_value(name)
        value = get_value(value)
        existsVar = self.get_var(name)
        with self.engine.connect() as conn:
            if existsVar != None:
               stmt = update(BaseTables.env_var).where(
                    (BaseTables.env_var.c.Name == name) &
                    (BaseTables.env_var.c.App == self.app_name)
               ).values(Value=value)
               conn.execute(stmt)
            else:
               ins = insert(BaseTables.env_var).values(App=self.app_name, Name=name, Value=value)
               conn.execute(ins)
            conn.commit()

    def delete_var(self, name : str):
        name = get_value(name)
        with self.engine.connect() as conn:
            stmt = delete(BaseTables.env_var).where((BaseTables.env_var.c.Name == name) & (BaseTables.env_var.c.App == self.app_name))
            conn.execute(stmt)
            conn.commit()

    def get_theme(self):
        data = self.select('system')
        if data:
            return System(data[0]).Theme
        else:
            with self.engine.connect() as conn:
                ins = insert(BaseTables.system).values(App=self.app_name, Tema='light')
                conn.execute(ins)
                conn.commit()
            return 'light'

    def update_theme(self, theme : str):
        theme = get_value(theme)
        _theme = self.get_theme()
        if _theme:
            with self.engine.connect() as conn:
                stmt = update(BaseTables.system).where(
                    BaseTables.system.c.App == self.app_name
                ).values(Tema=theme)
                conn.execute(stmt)
                conn.commit()
           

    




