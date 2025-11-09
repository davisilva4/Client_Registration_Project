from sqlite3 import connect, Error
from contextlib import closing

class Database():
    def __init__(self, db, parent_window=None):
        self.db = db
        self.parent = parent_window

    def _with_conn(self):
        """Helper: abre conexão e ativa foreign_keys; retorna conexão."""
        conn = connect(self.db)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_contractors_table(self):
        try:
            with closing(self._with_conn()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Contratantes(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Nome TEXT NOT NULL,
                            Sobrenome TEXT NOT NULL,
                            DataNascimento TEXT NOT NULL,
                            RG TEXT UNIQUE CHECK (LENGTH(RG) BETWEEN 7 AND 9),
                            CPF TEXT NOT NULL UNIQUE CHECK(LENGTH(CPF) = 11),
                            CEP TEXT NOT NULL CHECK(LENGTH(CEP) = 8),
                            Endereco TEXT NOT NULL,
                            Complemento TEXT,
                            Cidade TEXT NOT NULL,
                            Estado TEXT NOT NULL,
                            Telefone TEXT NOT NULL CHECK(LENGTH(Telefone) BETWEEN 8 AND 9)
                        );
                    """)
                conn.commit()
        except Error as e:
            print(f"Erro create_contractors_table: {e}")

    def create_students_table(self):
        try:
            with closing(self._with_conn()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Estudantes(
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
            print(f"Erro create_students_table: {e}")

    def create_contract_table(self):
        try:
            with closing(self._with_conn()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Contratos(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            CTR TEXT NOT NULL CHECK(LENGTH(CTR) BETWEEN 3 AND 5),
                            ID_Aluno INTEGER NOT NULL,
                            Valor REAL NOT NULL,
                            Taxa_Matricula REAL,
                            Duracao INT NOT NULL,
                            FOREIGN KEY (ID_Aluno) REFERENCES Estudantes(ID) ON DELETE CASCADE
                        );
                    """)
                conn.commit()
        except Error as e:
            print(f"Erro create_contract_table: {e}")

    def create_classe_table(self):
        try:
            with closing(self._with_conn()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Classes(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Professor TEXT NOT NULL,
                            Dia TEXT NOT NULL,
                            Hora TEXT NOT NULL
                        );
                    """)
                conn.commit()
        except Error as e:
            print(f"Erro create_classe_table: {e}")

    def create_servicos_table(self):
        try:
            with closing(self._with_conn()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Servicos(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ID_Contrato INTEGER NOT NULL,
                            Curso TEXT NOT NULL,
                            FOREIGN KEY (ID_Contrato) REFERENCES Contratos(ID) ON DELETE CASCADE
                        );
                    """)
                conn.commit()
        except Error as e:
            print(f"Erro create_servicos_table: {e}")

    def create_vigencias_table(self):
        try:
            with closing(self._with_conn()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Vigencias(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ID_Servico INTEGER NOT NULL,
                            Data_Inicio TEXT NOT NULL,
                            Data_Fim TEXT NOT NULL,
                            Status TEXT NOT NULL CHECK(Status IN ('Ativo', 'Cancelado', 'Suspenso', 'Encerrado', 'Renovado')),
                            FOREIGN KEY (ID_Servico) REFERENCES Servicos(ID) ON DELETE CASCADE
                        );
                    """)
        except Error as e:
            print(f"Erro create_vigencias_table: {e}")

    def create_agenda_table(self):
        try:
            with closing(self._with_conn()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Agenda(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ID_Servico INTEGER NOT NULL,
                            ID_Classe INTEGER NOT NULL,
                            Data_Entrada TEXT NOT NULL,
                            Data_Saida TEXT NOT NULL,
                            Status TEXT NOT NULL CHECK(Status IN ('Ativo', 'Removido', 'Transferido')),
                            FOREIGN KEY (ID_Servico) REFERENCES Servicos(ID) ON DELETE CASCADE,
                            FOREIGN KEY (ID_Classe) REFERENCES Classes(ID) ON DELETE CASCADE
                        );
                    """)
                conn.commit()
        except Error as e:
            print(f"Erro create_agenda_table: {e}")

    def create_all_tables(self):
        """Cria todas as tabelas na ordem correta."""
        self.create_contractors_table()
        self.create_students_table()
        self.create_contract_table()
        self.create_classe_table()
        self.create_servicos_table()
        self.create_vigencias_table()
        self.create_agenda_table()


