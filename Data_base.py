from sqlite3 import connect, Error
from contextlib import closing
from typing import Any, Iterable


class Database:
    """
    Classe responsável por gerenciar o banco de dados SQLite,
    incluindo criação de tabelas e inserção de dados.
    """

    def __init__(self, db: str, parent_window=None):
        self.db = db
        self.parent = parent_window

    # ============================================================
    # CONEXÃO
    # ============================================================

    def _with_conn(self):
        """Abre conexão com o banco e ativa suporte a foreign_keys."""
        conn = connect(self.db)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # ============================================================
    # CRIAÇÃO DE TABELAS
    # ============================================================

    def create_contractors_table(self):
        """Tabela de contratantes."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Contratantes (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Nome TEXT NOT NULL,
                        Sobrenome TEXT NOT NULL,
                        Data_Nascimento TEXT NOT NULL,
                        RG TEXT UNIQUE CHECK(LENGTH(RG) BETWEEN 7 AND 9),
                        CPF TEXT NOT NULL UNIQUE CHECK(LENGTH(CPF) = 11),
                        CEP TEXT NOT NULL CHECK(LENGTH(CEP) = 8),
                        Endereco TEXT NOT NULL,
                        Complemento TEXT,
                        Bairro TEXT NOT NULL,
                        Cidade TEXT NOT NULL,
                        Estado TEXT NOT NULL,
                        Telefone TEXT NOT NULL CHECK(LENGTH(Telefone) BETWEEN 8 AND 9)
                    );
                """)
                conn.commit()
        except Error as e:
            print(f"[ERRO] create_contractors_table: {e}")

    def create_students_table(self):
        """Tabela de estudantes vinculados a contratantes."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Estudantes (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ID_Contratante INTEGER NOT NULL,
                        Nome TEXT NOT NULL,
                        Sobrenome TEXT NOT NULL,
                        Data_Nascimento TEXT NOT NULL,
                        FOREIGN KEY (ID_Contratante) REFERENCES Contratantes(ID) ON DELETE CASCADE
                    );
                """)
                conn.commit()
        except Error as e:
            print(f"[ERRO] create_students_table: {e}")

    def create_contracts_table(self):
        """Tabela de contratos vinculados a estudantes."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Contratos (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ID_Aluno INTEGER NOT NULL,
                        CTR TEXT NOT NULL CHECK(LENGTH(CTR) BETWEEN 3 AND 5),
                        Valor REAL NOT NULL,
                        Taxa_Matricula REAL,
                        Duracao INT NOT NULL,
                        FOREIGN KEY (ID_Aluno) REFERENCES Estudantes(ID) ON DELETE CASCADE
                    );
                """)
                conn.commit()
        except Error as e:
            print(f"[ERRO] create_contracts_table: {e}")

    def create_classes_table(self):
        """Tabela de classes (professor, dia e hora)."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Classes (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Professor TEXT NOT NULL,
                        Dia TEXT NOT NULL,
                        Hora TEXT NOT NULL
                    );
                """)
                conn.commit()
        except Error as e:
            print(f"[ERRO] create_classes_table: {e}")

    def create_services_table(self):
        """Tabela de serviços vinculados a contratos."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Servicos (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ID_Contrato INTEGER NOT NULL,
                        Curso TEXT NOT NULL,
                        FOREIGN KEY (ID_Contrato) REFERENCES Contratos(ID) ON DELETE CASCADE
                    );
                """)
                conn.commit()
        except Error as e:
            print(f"[ERRO] create_services_table: {e}")

    def create_validities_table(self):
        """Tabela de vigências vinculadas a serviços."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Vigencias (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ID_Servico INTEGER NOT NULL,
                        Data_Inicio TEXT NOT NULL,
                        Data_Fim TEXT,
                        Status TEXT NOT NULL CHECK(Status IN (
                            'Ativo', 'Cancelado', 'Suspenso', 'Encerrado', 'Renovado'
                        )),
                        FOREIGN KEY (ID_Servico) REFERENCES Servicos(ID) ON DELETE CASCADE
                    );
                """)
                conn.commit()
        except Error as e:
            print(f"[ERRO] create_validities_table: {e}")

    def create_schedules_table(self):
        """Tabela de agendas (ligando serviços e classes)."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Agendas (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ID_Servico INTEGER NOT NULL,
                        ID_Classe INTEGER NOT NULL,
                        Data_Entrada TEXT NOT NULL,
                        Data_Saida TEXT,
                        Status TEXT NOT NULL CHECK(Status IN ('Ativo', 'Removido', 'Transferido')),
                        FOREIGN KEY (ID_Servico) REFERENCES Servicos(ID) ON DELETE CASCADE,
                        FOREIGN KEY (ID_Classe) REFERENCES Classes(ID) ON DELETE CASCADE
                    );
                """)
                conn.commit()
        except Error as e:
            print(f"[ERRO] create_schedules_table: {e}")

    def create_all_tables(self):
        """Cria todas as tabelas na ordem correta."""
        self.create_contractors_table()
        self.create_students_table()
        self.create_contracts_table()
        self.create_classes_table()
        self.create_services_table()
        self.create_validities_table()
        self.create_schedules_table()

    # ============================================================
    # INSERÇÃO DE DADOS
    # ============================================================

    def insert_data(self, table: str, columns: Iterable[str], values: Iterable[Any]):
        """Insere dados genéricos em qualquer tabela."""
        try:
            with closing(self._with_conn()) as conn, closing(conn.cursor()) as cursor:
                placeholders = ", ".join(["?"] * len(values))
                sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(values))
                conn.commit()
        except Error as e:
            print(f"[ERRO] insert_data em {table}: {e}")

    # ============================================================
    # INSERÇÕES ESPECÍFICAS (facilitadores)
    # ============================================================

    def insert_contractor(self, data: tuple[str, ...]):
        """Insere contratante."""
        cols = ["Nome", "Sobrenome", "Data_Nascimento", "RG", "CPF", "CEP",
                "Endereco", "Complemento", "Bairro", "Cidade", "Estado", "Telefone"]
        self.insert_data("Contratantes", cols, data)

    def insert_student(self, id_contratante: int, data: tuple[str, str, str]):
        """Insere estudante vinculado a um contratante."""
        cols = ["ID_Contratante", "Nome", "Sobrenome", "Data_Nascimento"]
        self.insert_data("Estudantes", cols, (id_contratante, *data))

    def insert_contract(self, id_aluno: int, data: tuple[str, float, float, int]):
        """Insere contrato vinculado a um aluno."""
        cols = ["ID_Aluno", "CTR", "Valor", "Taxa_Matricula", "Duracao"]
        self.insert_data("Contratos", cols, (id_aluno, *data))

    def insert_class(self, data: tuple[str, str, str]):
        """Insere uma classe."""
        cols = ["Professor", "Dia", "Hora"]
        self.insert_data("Classes", cols, data)

    def insert_service(self, id_contrato: int, data: tuple[str]):
        """Insere serviço vinculado a um contrato."""
        cols = ["ID_Contrato", "Curso"]
        self.insert_data("Servicos", cols, (id_contrato, *data))

    def insert_schedule(self, id_servico: int, id_classe: int, data: tuple[str, str]):
        """Insere entrada na agenda."""
        cols = ["ID_Servico", "ID_Classe", "Data_Entrada", "Status"]
        self.insert_data("Agendas", cols, (id_servico, id_classe, *data))



    

    
    

