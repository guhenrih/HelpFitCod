# backEnd.py
"""
Módulo de backend para a aplicação HelpFit.
Implementa lógica de persistência em SQLite e análise com pandas e numpy.
Inclui migração de schema automática para novas colunas.
"""
import sqlite3
from sqlite3 import Connection
from datetime import datetime, date
import pandas as pd
import numpy as np

DB_FILE = 'helpfit.db'

# -------------------------------------------------------------
# Conexão com banco
# -------------------------------------------------------------
def get_connection() -> Connection:
    """
    Abre conexão com SQLite, garantindo foreign_keys ativadas.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# -------------------------------------------------------------
# Inicialização e migração do banco
# -------------------------------------------------------------
def init_db():
    """
    Cria tabelas essenciais se não existirem e aplica migração de schema.
    - students: alunos
    - attendance: frequência
    - justifications: justificativas de faltas
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela students
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            data_matricula TEXT NOT NULL,
            telefone TEXT,
            sexo TEXT,
            comorbidade TEXT,
            dias_contratados INTEGER NOT NULL,
            valor_plano REAL NOT NULL,
            data_nascimento TEXT
        );
    ''')

    # Tabela attendance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            present INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    ''')

    # Tabela justifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS justifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            reason TEXT,
            canceled INTEGER,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    ''')

    # Índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_cpf ON students(cpf);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_just_student ON justifications(student_id);')

    conn.commit()
    conn.close()

# -------------------------------------------------------------
# CRUD de alunos
# -------------------------------------------------------------
def add_student(
    nome: str,
    cpf: str,
    data_matricula: str,
    dias_contratados: int,
    valor_plano: float,
    data_nascimento: str = None,
    telefone: str = None,
    sexo: str = None,
    comorbidade: str = None
) -> dict:
    init_db()
    student_id = f"STU{int(datetime.now().timestamp())}"
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        '''
        INSERT INTO students (
            id, nome, cpf, data_matricula, data_nascimento,
            telefone, sexo, comorbidade, dias_contratados, valor_plano
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''',
        (
            student_id, nome, cpf, data_matricula, data_nascimento,
            telefone, sexo, comorbidade, dias_contratados, valor_plano
        )
    )
    conn.commit()
    conn.close()
    return get_student_full(cpf)

def get_student_by_cpf(cpf: str) -> dict:
    return get_student_full(cpf)

def delete_student(cpf: str) -> bool:
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE cpf = ?;', (cpf,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

# -------------------------------------------------------------
# Frequência e justificativas
# -------------------------------------------------------------
def record_attendance(student_id: str, date_str: str, present: bool) -> None:
    """
    Registra presença (present=True) ou falta (present=False) no dia especificado.
    date_str deve estar no formato 'YYYY-MM-DD'.
    """
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO attendance (student_id, date, present) VALUES (?, ?, ?);',
        (student_id, date_str, int(present))
    )
    conn.commit()
    conn.close()

def justify_absence(student_id: str, date_str: str, reason: str, canceled: bool) -> None:
    """
    Insere uma justificativa de falta para o aluno.
    'canceled' indica se o aluno cancelou a presença.
    """
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        '''
        INSERT INTO justifications (student_id, date, reason, canceled)
        VALUES (?, ?, ?, ?);
        ''',
        (student_id, date_str, reason, int(canceled))
    )
    conn.commit()
    conn.close()

def get_attendance_history(student_id: str) -> pd.DataFrame:
    """
    Retorna DataFrame com histórico de presença/falta e justificativas.
    """
    init_db()
    conn = get_connection()
    df_att = pd.read_sql_query(
        '''
        SELECT a.date, a.present, j.reason, j.canceled
        FROM attendance a
        LEFT JOIN justifications j
          ON a.student_id = j.student_id AND a.date = j.date
        WHERE a.student_id = ?
        ORDER BY a.date;
        ''',
        conn,
        params=(student_id,),
        parse_dates=['date']
    )
    conn.close()
    return df_att

# -------------------------------------------------------------
# Informações e cálculo de evasão
# -------------------------------------------------------------
def get_student_full(cpf: str) -> dict:
    init_db()
    conn = get_connection()
    student_df = pd.read_sql_query(
        'SELECT * FROM students WHERE cpf = ?;', conn,
        params=(cpf,), parse_dates=['data_matricula', 'data_nascimento']
    )
    if student_df.empty:
        conn.close()
        return None
    student = student_df.iloc[0]
    attendance_df = pd.read_sql_query(
        'SELECT present FROM attendance WHERE student_id = ?;',
        conn, params=(student.id,)
    )
    conn.close()
    dias_presentes = int(attendance_df['present'].sum())
    dias_faltas = len(attendance_df) - dias_presentes
    total_contratado = student.dias_contratados
    chance_evasao = round((dias_faltas / total_contratado) * 100, 2) if total_contratado > 0 else 0.0
    today = date.today()
    idade = None
    if pd.notna(student.data_nascimento):
        dn = student.data_nascimento
        idade = today.year - dn.year - ((today.month, today.day) < (dn.month, dn.day))
    dm = student.data_matricula
    meses = (today.year - dm.year)*12 + today.month - dm.month
    status = 'Ativo' if dias_presentes >= total_contratado * 0.5 else 'Inativo'
    return {
        'id': student.id,
        'nome': student.nome,
        'cpf': student.cpf,
        'telefone': student.telefone,
        'data_matricula': student.data_matricula.strftime('%Y-%m-%d'),
        'data_nascimento': (
            student.data_nascimento.strftime('%Y-%m-%d') if pd.notna(student.data_nascimento) else None
        ),
        'idade': idade,
        'dias_contratados': int(total_contratado),
        'dias_presentes': dias_presentes,
        'dias_faltas': dias_faltas,
        'status_matricula': status,
        'tempo_matricula_meses': meses,
        'chance_evasao_percent': chance_evasao,
        'valor_plano': float(student.valor_plano)
    }

# -------------------------------------------------------------
# Execução direta
# -------------------------------------------------------------
if __name__ == '__main__':
    init_db()
    print('Banco de dados helpfit.db inicializado e migrado!')
