# backEnd.py
"""
Módulo de backend para a aplicação HelpFit.
Implementa lógica de persistência em SQLite e análise com pandas, numpy e scikit-learn.
As funcionalidades são separadas por área de página:
  - Cadastro de alunos
  - Registro de frequência
  - Obtenção de informações e estatísticas
  - Exclusão de alunos
"""
import sqlite3
from sqlite3 import Connection
from datetime import datetime, date
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

DB_FILE = 'helpfit.db'

# -------------------------------------------------------------
# Conexão e inicialização do banco
# -------------------------------------------------------------
def get_connection() -> Connection:
    """
    Abre conexão com SQLite, garantindo foreign_keys ativadas.
    Retorna conexão.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Cria as tabelas essenciais se ainda não existirem:
      - students: armazena dados pessoais e contratuais
      - attendance: armazena registros de presença/falta
    Adiciona índices para melhorar performance de consulta.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de alunos
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            data_matricula TEXT NOT NULL,
            data_nascimento TEXT,
            telefone TEXT,
            sexo TEXT,
            comorbidade TEXT,
            dias_contratados INTEGER NOT NULL,
            valor_plano REAL NOT NULL
        );
        '''
    )
    # Tabela de frequência
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            present INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        '''
    )

    # Índices para buscas rápidas
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_cpf ON students(cpf);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);')

    conn.commit()
    conn.close()

# -------------------------------------------------------------
# Backend da página de Cadastro (CadastroPage)
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
    """
    Insere um novo aluno na tabela 'students'.
    Recebe campos obrigatórios e opcionais.
    Gera ID baseado em timestamp.
    Retorna dict com dados completos do aluno (via get_student_full).
    """
    init_db()
    # Gerar ID único
    student_id = f"STU{int(datetime.now().timestamp())}"

    # Inserir no banco
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

    # Retornar dados completos do aluno cadastrado
    return get_student_full(cpf)

# -------------------------------------------------------------
# Backend da página de Frequência (FrequenciaPage)
# -------------------------------------------------------------
def record_attendance(student_id: str, date_str: str, present: bool) -> None:
    """
    Registra presença (present=True) ou falta (present=False).
    Armazena em 'attendance': student_id, data e status presente.
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

# -------------------------------------------------------------
# Backend da página de Informações (InformacoesPage)
# -------------------------------------------------------------
def get_student_full(cpf: str) -> dict:
    """
    Recupera dados completos do aluno e estatísticas de frequência.
    - Carrega dados pessoais da tabela students
    - Carrega histórico de attendance
    - Usa pandas para processar datas e agregações
    - Usa scikit-learn LogisticRegression para estimar chance de evasão
    Retorna dict com todos os campos solicitados.
    """
    init_db()
    conn = get_connection()

    # Carregar dados do aluno em DataFrame
    student_df = pd.read_sql_query(
        'SELECT * FROM students WHERE cpf = ?;',
        conn,
        params=(cpf,),
        parse_dates=['data_matricula', 'data_nascimento']
    )
    if student_df.empty:
        conn.close()
        return None
    student = student_df.iloc[0]

    # Carregar histórico de attendance em DataFrame
    attendance_df = pd.read_sql_query(
        'SELECT date, present FROM attendance WHERE student_id = ?;',
        conn,
        params=(student.id,),
        parse_dates=['date']
    )
    conn.close()

    # --------- Cálculos estatísticos ---------
    # Idade
    if pd.notna(student.data_nascimento):
        today = pd.to_datetime(date.today())
        idade = (
            today.year - student.data_nascimento.year
            - ((today.month, today.day) < (student.data_nascimento.month, student.data_nascimento.day))
        )
    else:
        idade = None

    # Tempo de matrícula em meses
    today = pd.to_datetime(date.today())
    months = (
        (today.year - student.data_matricula.year) * 12
        + today.month - student.data_matricula.month
    )

    # Frequência do mês atual
    attendance_df['mes'] = attendance_df['date'].dt.to_period('M')
    current_period = today.to_period('M')
    df_current = attendance_df[attendance_df['mes'] == current_period]
    dias_presentes = int(df_current['present'].sum())
    dias_faltas = int(student.dias_contratados - dias_presentes)

    # Preparar dados para modelo de evasão
    # Agrupar por mês e calcular presentes, faltas
    agg = attendance_df.groupby('mes').agg(
        presentes=('present', 'sum'), total=('present', 'count')
    ).reset_index()
    agg['faltas'] = agg['total'] - agg['presentes']
    # Criar variável alvo simplificada: churn=1 se faltas>metade dos dias contratados
    agg['churn'] = (agg['faltas'] > student.dias_contratados / 2).astype(int)

    # Treinar modelo se houver dados suficientes
    model = LogisticRegression()
    if len(agg) >= 2:
        X = agg[['presentes', 'faltas']]
        y = agg['churn']
        model.fit(X, y)
        prob = model.predict_proba([[dias_presentes, dias_faltas]])[0][1]
        chance_evasao = round(float(prob * 100), 2)
    else:
        # Fallback direto sem modelo
        chance_evasao = round((dias_faltas / student.dias_contratados) * 100, 2)

    # Status de matrícula baseado em 50% de presença
    status = 'Ativo' if dias_presentes >= student.dias_contratados * 0.5 else 'Inativo'

    # Montar dict de saída
    return {
        'id': student.id,
        'nome': student.nome,
        'cpf': student.cpf,
        'data_matricula': student.data_matricula.strftime('%Y-%m-%d'),
        'data_nascimento': (
            student.data_nascimento.strftime('%Y-%m-%d')
            if pd.notna(student.data_nascimento) else None
        ),
        'idade': idade,
        'sexo': student.sexo,
        'comorbidade': student.comorbidade,
        'dias_contratados': int(student.dias_contratados),
        'dias_presentes': dias_presentes,
        'dias_faltas': dias_faltas,
        'status_matricula': status,
        'tempo_matricula_meses': int(months),
        'chance_evasao_percent': chance_evasao,
        'valor_plano': float(student.valor_plano)
    }

# -------------------------------------------------------------
# Backend da página de Exclusão (InformacoesPage -> Excluir)
# -------------------------------------------------------------
def delete_student(cpf: str) -> bool:
    """
    Remove o aluno identificado pelo CPF e seus registros de attendance.
    Retorna True se removeu, False se não encontrado.
    """
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE cpf = ?;', (cpf,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

# -------------------------------------------------------------
# Execução direta para inicializar o DB
# -------------------------------------------------------------
if __name__ == '__main__':
    init_db()
    print('Banco de dados helpfit.db inicializado!')
