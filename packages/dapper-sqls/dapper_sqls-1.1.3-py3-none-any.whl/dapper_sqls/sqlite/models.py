# coding: utf-8
from sqlalchemy import MetaData, Table, Column, Integer, String

class BaseTables:
    meta_data = MetaData()
    system = Table(
        'system', meta_data,
        Column('id', Integer, primary_key=True),
        Column('App', String),
        Column('Tema', String)
    )
    env_var = Table(
        'env_var', meta_data,
        Column('id', Integer, primary_key=True),
        Column('App', String),
        Column('Name', String),
        Column('Value', String)
    )
    path = Table(
        'path', meta_data,
        Column('id', Integer, primary_key=True),
        Column('App', String),
        Column('Name', String),
        Column('Path', String)
    )

class BaseTableModel(object):
    def __init__(self, dados : dict):
        self.id : int = dados['id']
        self.App : str = dados['App'] 

class Path(BaseTableModel):
    def __init__(self, dados : dict):
       super().__init__(dados)
       self.Name : str = dados['Name']
       self.Path : str = dados['Path']

class EnvVar(BaseTableModel):
    
    def __init__(self, dados : dict):
       super().__init__(dados)
       self.Name : str = dados['Name']
       self.Value : str = dados['Value']

class System(BaseTableModel):
    def __init__(self, dados : dict):
       super().__init__(dados)
       self.Theme : str = dados['Tema']




   
    


