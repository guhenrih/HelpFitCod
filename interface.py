# interface.py
"""
Aplicação HelpFit - Interface Gráfica

Este módulo define a interface de usuário usando Tkinter,
com navegação entre páginas, paleta de cores personalizada e
widgets organizados para cada funcionalidade.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from datetime import datetime, date
from backEnd import *




# -------------------------------------------------------------
# Paleta de cores
# -------------------------------------------------------------
PALETTE = [
    "#4535CF",  # Azul principal para botões
    "#4F46A5",  # Fundo da barra de navegação
    "#2D16FA",  # Fundo de frames secundários
    "#4D487A",  # Fundo de LabelFrames
    "#3E3C50",  # Cor ativa (hover/pressed)
    "#32313B",  # Fundo geral da janela
]
BUTTON_BG    = PALETTE[0]
BUTTON_FG    = "white"
NAV_BG       = PALETTE[1]
FRAME_BG     = PALETTE[2]
LF_BG        = PALETTE[3]
LF_FG        = "white"
BG_COLOR     = PALETTE[5]

# -------------------------------------------------------------
# Classe principal da aplicação
# -------------------------------------------------------------
class HelpFitApp(tk.Tk):
    """
    Janela principal que gerencia a navegação e exibição de páginas.
    Herdada de tk.Tk.
    """
    def __init__(self):
        super().__init__()
        # Configurações da janela
        self.title("HelpFit")
        self.geometry("900x650")
        self.configure(bg=BG_COLOR)

        # Configura grid principal para que o container cresça
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Criar barra de navegação no topo
        nav = tk.Frame(self, bg=NAV_BG, bd=2, relief=tk.RAISED)
        nav.grid(row=0, column=0, sticky="ew")
        pages = ["Inicio", "Cadastro", "Frequencia", "Relatorio", "Informacoes", "Perfil", "Login"]
        # Criar botão para cada página e configurar ação de troca de frame
        for idx, page in enumerate(pages):
            btn = tk.Button(
                nav,
                text=page,
                bg=BUTTON_BG,
                fg=BUTTON_FG,
                activebackground=PALETTE[4],
                command=lambda p=page: self.show_frame(p)
            )
            btn.grid(row=0, column=idx, padx=2, pady=2, sticky="ew")
            nav.columnconfigure(idx, weight=1)

        # Container principal onde os frames das páginas serão empilhados
        container = tk.Frame(self, bg=BG_COLOR)
        container.grid(row=1, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Dicionário para armazenar instâncias de cada página
        self.frames = {}
        page_classes = {
            "Inicio":       InicioPage,
            "Cadastro":     CadastroPage,
            "Frequencia":    FrequenciaPage,
            "Relatorio":    RelatorioPage,
            "Informacoes":  InformacoesPage,
            "Perfil":       PerfilPage,
            "Login":        LoginPage,
        }
        # Instancia todas as páginas e as empilha no container
        for name, PageClass in page_classes.items():
            frame = PageClass(parent=container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Exibir página inicial por padrão
        self.show_frame("Inicio")

    def show_frame(self, page_name):
        """
        Traz o frame da página selecionada ao topo.
        """
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()


# -------------------------------------------------------------
# LabelFrame customizado com estilo
# -------------------------------------------------------------
class StyledLabelFrame(tk.LabelFrame):
    """
    LabelFrame com cores personalizadas da paleta.
    Usado para destacar grupos de widgets.
    """
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, text=text, bg=LF_BG, fg=LF_FG, labelanchor='n', **kwargs)
        self.configure(highlightbackground=LF_FG)


# -------------------------------------------------------------
# Páginas da aplicação
# -------------------------------------------------------------

class InicioPage(tk.Frame):
    """
    Página inicial com botões grandes para navegar entre as funcionalidades.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        # Container central para botões
        main = tk.Frame(self, bg=BG_COLOR)
        main.place(relx=0.5, rely=0.5, anchor='center')

        # Configurar grid interno de 3x2
        for i in range(3): main.rowconfigure(i, weight=1)
        for j in range(2): main.columnconfigure(j, weight=1)

        # Lista de páginas para botões
        buttons = ["Informacoes", "Cadastro", "Perfil", "Frequencia", "Login", "Relatorio"]
        for idx, name in enumerate(buttons):
            btn = tk.Button(
                main,
                text=name,
                bg=BUTTON_BG,
                fg=BUTTON_FG,
                activebackground=PALETTE[4],
                font=(None, 14),
                width=20,
                command=lambda p=name: controller.show_frame(p)
            )
            # Posiciona em grid 2 colunas, 3 linhas
            btn.grid(row=idx//2, column=idx%2, padx=15, pady=15, sticky="nsew")

class CadastroPage(tk.Frame):
    """
    Página de cadastro de um novo aluno.
    Usa um picker de data customizado em Tkinter sem depender de bibliotecas externas.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Layout em duas colunas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Esquerda: dados básicos
        left = tk.Frame(self, bg=BG_COLOR)
        left.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        left.columnconfigure(0, weight=1)

        tk.Label(left, text="NOME*", bg=BG_COLOR, fg=LF_FG).grid(row=0, column=0, sticky="w")
        self.entry_nome = tk.Entry(left)
        self.entry_nome.grid(row=1, column=0, sticky="ew", pady=(0,10))

        tk.Label(left, text="CPF*", bg=BG_COLOR, fg=LF_FG).grid(row=2, column=0, sticky="w")
        self.entry_cpf = tk.Entry(left)
        self.entry_cpf.grid(row=3, column=0, sticky="ew", pady=(0,10))

        tk.Label(left, text="DATA MATRÍCULA*", bg=BG_COLOR, fg=LF_FG).grid(row=4, column=0, sticky="w")
        frame_mat = tk.Frame(left, bg=BG_COLOR)
        frame_mat.grid(row=5, column=0, sticky="ew", pady=(0,10))
        frame_mat.columnconfigure(0, weight=1)
        self.entry_data_matricula = tk.Entry(frame_mat)
        self.entry_data_matricula.grid(row=0, column=0, sticky="ew")
        tk.Button(frame_mat, text="📅", bg=BUTTON_BG, fg=BUTTON_FG,
                  command=lambda: self.open_date_picker(self.entry_data_matricula)).grid(row=0, column=1, padx=(5,0))

        tk.Label(left, text="DIAS POR MÊS CONTRATADOS*", bg=BG_COLOR, fg=LF_FG).grid(row=6, column=0, sticky="w")
        self.entry_dias_contratados = tk.Entry(left)
        self.entry_dias_contratados.grid(row=7, column=0, sticky="ew", pady=(0,10))

        tk.Label(left, text="VALOR PLANO*", bg=BG_COLOR, fg=LF_FG).grid(row=8, column=0, sticky="w")
        self.entry_valor_plano = tk.Entry(left)
        self.entry_valor_plano.grid(row=9, column=0, sticky="ew", pady=(0,10))

        # Direita: dados adicionais
        right = tk.Frame(self, bg=BG_COLOR)
        right.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        right.columnconfigure(0, weight=1)

        tk.Label(right, text="DATA NASCIMENTO*", bg=BG_COLOR, fg=LF_FG).grid(row=0, column=0, sticky="w")
        frame_nasc = tk.Frame(right, bg=BG_COLOR)
        frame_nasc.grid(row=1, column=0, sticky="ew", pady=(0,10))
        frame_nasc.columnconfigure(0, weight=1)
        self.entry_data_nasc = tk.Entry(frame_nasc)
        self.entry_data_nasc.grid(row=0, column=0, sticky="ew")
        tk.Button(frame_nasc, text="📅", bg=BUTTON_BG, fg=BUTTON_FG,
                  command=lambda: self.open_date_picker(self.entry_data_nasc)).grid(row=0, column=1, padx=(5,0))

        tk.Label(right, text="TELEFONE*", bg=BG_COLOR, fg=LF_FG).grid(row=2, column=0, sticky="w")
        self.entry_telefone = tk.Entry(right)
        self.entry_telefone.grid(row=3, column=0, sticky="ew", pady=(0,10))

        tk.Label(right, text="SEXO", bg=BG_COLOR, fg=LF_FG).grid(row=4, column=0, sticky="w")
        self.entry_sexo = tk.Entry(right)
        self.entry_sexo.grid(row=5, column=0, sticky="ew", pady=(0,10))

        tk.Label(right, text="COMORBIDADE?", bg=BG_COLOR, fg=LF_FG).grid(row=6, column=0, sticky="w")
        self.entry_comorbidade = tk.Entry(right)
        self.entry_comorbidade.grid(row=7, column=0, sticky="ew", pady=(0,10))

        tk.Button(
            self, text="Cadastrar", bg=BUTTON_BG, fg=BUTTON_FG,
            activebackground=PALETTE[4], width=15,
            command=self.on_register
        ).grid(row=1, column=0, columnspan=2, pady=10)

    def open_date_picker(self, entry_widget):
        """
        Abre uma janela de seleção de data simples.
        """
        top = tk.Toplevel(self)
        top.title("Selecione a data")
        cal = tk.Frame(top)
        cal.pack(padx=10, pady=10)

        # Comboboxes para dia, mês e ano
        import calendar
        days = list(range(1,32))
        months = list(calendar.month_name)[1:]
        current_year = date.today().year
        years = list(range(current_year-100, current_year+1))

        var_d = tk.IntVar(value=date.today().day)
        var_m = tk.StringVar(value=months[date.today().month-1])
        var_y = tk.IntVar(value=current_year)

        tk.Label(cal, text="Dia").grid(row=0, column=0)
        tk.OptionMenu(cal, var_d, *days).grid(row=1, column=0)
        tk.Label(cal, text="Mês").grid(row=0, column=1)
        tk.OptionMenu(cal, var_m, *months).grid(row=1, column=1)
        tk.Label(cal, text="Ano").grid(row=0, column=2)
        tk.OptionMenu(cal, var_y, *years).grid(row=1, column=2)

        def select():
            m_index = months.index(var_m.get())+1
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, f"{var_d.get():02d}/{m_index:02d}/{var_y.get()}")
            top.destroy()

        tk.Button(top, text="OK", command=select).pack(pady=(5,10))

    def on_register(self):
        """
        Captura valores, converte datas ISO, chama add_student e limpa campos.
        """
        nome = self.entry_nome.get().strip()
        cpf = self.entry_cpf.get().strip()
        dmat = self.entry_data_matricula.get().strip()
        dnasc = self.entry_data_nasc.get().strip()
        tel = self.entry_telefone.get().strip()

        # Converter datas
        try:
            dm = datetime.strptime(dmat, "%d/%m/%Y").strftime("%Y-%m-%d")
            dn = datetime.strptime(dnasc, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            tk.messagebox.showerror("Data Inválida", "Use DD/MM/YYYY para as datas.")
            return

        try:
            dias = int(self.entry_dias_contratados.get().strip())
            valor = float(self.entry_valor_plano.get().strip())
            aluno = add_student(
                nome, cpf, dm, dias, valor,
                data_nascimento=dn, telefone=tel,
                sexo=self.entry_sexo.get().strip(),
                comorbidade=self.entry_comorbidade.get().strip()
            )
            tk.messagebox.showinfo("Sucesso", f"Aluno {aluno['nome']} cadastrado!")
            for e in [self.entry_nome, self.entry_cpf, self.entry_data_matricula,
                      self.entry_data_nasc, self.entry_telefone,
                      self.entry_dias_contratados, self.entry_valor_plano,
                      self.entry_sexo, self.entry_comorbidade]:
                e.delete(0, tk.END)
        except Exception as ex:
            tk.messageebox.showerror("Erro ao cadastrar", str(ex))

class FrequenciaPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        tk.Label(self, text="CPF do aluno:", bg='white').grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_cpf = tk.Entry(self)
        self.entry_cpf.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Data (DD/MM/AAAA):", bg='white').grid(row=1, column=0, sticky="w", padx=10, pady=5)
        frame_data = tk.Frame(self, bg='white')
        frame_data.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.entry_data = tk.Entry(frame_data)
        self.entry_data.grid(row=0, column=0)
        tk.Button(
            frame_data, text="📅", command=lambda: self.open_date_picker(self.entry_data)
        ).grid(row=0, column=1, padx=(5, 0))

        tk.Button(self, text="Registrar Presença", command=self.on_record).grid(row=2, column=0, columnspan=2, pady=10)

    def open_date_picker(self, entry_widget):
        top = tk.Toplevel(self)
        top.title("Selecione a data")
        import calendar
        days = list(range(1,32))
        months = list(calendar.month_name)[1:]
        current_year = date.today().year
        years = list(range(current_year-50, current_year+1))

        var_d = tk.IntVar(value=date.today().day)
        var_m = tk.StringVar(value=months[date.today().month-1])
        var_y = tk.IntVar(value=current_year)

        frm = tk.Frame(top)
        frm.pack(padx=10, pady=10)
        tk.OptionMenu(frm, var_d, *days).grid(row=0, column=0)
        tk.OptionMenu(frm, var_m, *months).grid(row=0, column=1)
        tk.OptionMenu(frm, var_y, *years).grid(row=0, column=2)

        def select():
            m_index = months.index(var_m.get()) + 1
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, f"{var_d.get():02d}/{m_index:02d}/{var_y.get()}")
            top.destroy()

        tk.Button(top, text="OK", command=select).pack(pady=5)

    def on_record(self):
        cpf = self.entry_cpf.get().strip()
        date_str = self.entry_data.get().strip()
        try:
            date_iso = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            tk.messagebox.showerror("Data inválida", "Use o formato DD/MM/AAAA")
            return

        aluno = get_student_by_cpf(cpf)
        if not aluno:
            tk.messagebox.showerror("Erro", "Aluno não encontrado.")
            return

        try:
            record_attendance(aluno['id'], date_iso, present=True)
            tk.messagebox.showinfo("Sucesso", "Presença registrada com sucesso!")
            self.entry_cpf.delete(0, tk.END)
            self.entry_data.delete(0, tk.END)
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Falha ao registrar presença: {e}")



class RelatorioPage(tk.Frame):
    """
    Página para visualização de relatórios de evasão gerados por IA.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        # Configurar área de texto expansível
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        tk.Label(
            self,
            text="Relatório de Previsão de Evasão feito com IA",
            font=(None, 16),
            bg=BG_COLOR,
            fg=LF_FG
        ).grid(row=0, column=0, pady=10)
        txt = tk.Text(self)
        txt.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        tk.Button(
            self,
            text="Gerar Relatório",
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=PALETTE[4]
        ).grid(row=2, column=0, pady=10)


# --- Em interface.py ---

class InformacoesPage(tk.Frame):
    """
    Página de busca de aluno. Exibe dados, chance de evasão e exclusão via senha.
    O campo de senha aparece somente quando o botão 'Excluir Aluno' é clicado.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Barra de pesquisa
        search_frame = tk.Frame(self, bg=BG_COLOR)
        search_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        search_frame.columnconfigure(1, weight=1)
        tk.Label(search_frame, text="Buscar (CPF):", bg=BG_COLOR, fg=LF_FG).grid(row=0, column=0, sticky="w")
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(
            search_frame,
            text="Pesquisar",
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=PALETTE[4],
            command=self.on_search
        ).grid(row=0, column=2, padx=5)

        # Painel de informações
        info_frame = tk.Frame(self, relief=tk.SOLID, borderwidth=1,
                              bg=FRAME_BG, padx=10, pady=10)
        info_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        info_frame.columnconfigure(1, weight=1)

        # Campos de exibição
        self.info_labels = {}
        fields = ["ID:", "Nome:", "CPF:", "Data Matrícula:",
                  "Dias Contratados:", "Valor Plano:", "Telefone:", "Chance de Evasão:"]
        for idx, label_text in enumerate(fields):
            tk.Label(info_frame, text=label_text, bg=FRAME_BG, fg=LF_FG).grid(row=idx, column=0, sticky="w", pady=2)
            val_lbl = tk.Label(info_frame, text="", bg=FRAME_BG, fg=LF_FG)
            val_lbl.grid(row=idx, column=1, sticky="w", pady=2)
            self.info_labels[label_text] = val_lbl

        # Botão Excluir (inicia fluxo de senha)
        self.btn_delete = tk.Button(
            info_frame,
            text="Excluir Aluno",
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=PALETTE[4],
            command=self.show_password_field
        )
        self.btn_delete.grid(row=len(fields), column=0, columnspan=2, pady=(10,0))

        # Campo senha e botão confirmar (ocultos)
        self.pass_label = tk.Label(info_frame, text="Senha:", bg=FRAME_BG, fg=LF_FG)
        self.pass_entry = tk.Entry(info_frame, show="*")
        self.confirm_btn = tk.Button(
            info_frame,
            text="Confirmar Exclusão",
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=PALETTE[4],
            command=self.on_delete_confirm
        )

        # Ocultar inicialmente
        self.pass_label.grid_remove()
        self.pass_entry.grid_remove()
        self.confirm_btn.grid_remove()
        self.info_frame = info_frame

    def on_search(self):
        cpf = self.search_entry.get().strip()
        aluno = get_student_by_cpf(cpf)
        if not aluno:
            tk.messagebox.showerror("Não encontrado", "CPF não cadastrado.")
            return
        # Preencher campos
        mapping = {
            "ID:": aluno['id'],
            "Nome:": aluno['nome'],
            "CPF:": aluno['cpf'],
            "Data Matrícula:": aluno['data_matricula'],
            "Dias Contratados:": str(aluno['dias_contratados']),
            "Valor Plano:": f"{aluno['valor_plano']:.2f}",
            "Telefone:": aluno.get('telefone', ''),
            "Chance de Evasão:": f"{aluno['chance_evasao_percent']:.2f}%"
        }
        for key, val in mapping.items():
            self.info_labels[key].configure(text=val)
        self.info_frame.grid()

    def show_password_field(self):
        # Exibe o campo de senha e botão de confirmação
        total = len(self.info_labels)
        self.pass_label.grid(row=total, column=0, pady=(5,2))
        self.pass_entry.grid(row=total, column=1, pady=(5,2))
        self.confirm_btn.grid(row=total+1, column=0, columnspan=2, pady=(2,10))

    def on_delete_confirm(self):
        senha = self.pass_entry.get()
        if senha != "Helpfitmestra":
            tk.messagebox.showerror("Senha incorreta", "Senha mestra inválida.")
            return
        cpf = self.search_entry.get().strip()
        sucesso = delete_student(cpf)
        if sucesso:
            tk.messagebox.showinfo("Excluído", "Aluno removido com sucesso.")
            self.info_frame.grid_remove()
        else:
            tk.messagebox.showerror("Erro", "Falha ao excluir aluno.")



class PerfilPage(tk.Frame):
    """
    Página com informações do funcionário autenticado.
    Campos apenas leitura.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        # Formulário centralizado
        form = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        form.place(relx=0.5, rely=0.5, anchor='center')
        form.columnconfigure(1, weight=1)
        tk.Label(
            form,
            text="Informações Funcionário",
            font=(None, 16),
            bg=BG_COLOR,
            fg=LF_FG
        ).grid(row=0, column=0, columnspan=2, pady=(0,15))
        labels = ["Nome:", "Matrícula:", "Senha:"]
        for idx, text in enumerate(labels):
            tk.Label(
                form,
                text=text,
                bg=BG_COLOR,
                fg=LF_FG
            ).grid(row=idx+1, column=0, sticky="e", padx=5, pady=5)
            ent = tk.Entry(form, state='disabled', width=30)
            if text == "Senha":
                ent.config(show='*')
            ent.grid(row=idx+1, column=1, sticky="ew", padx=5, pady=5)


class LoginPage(tk.Frame):
    """
    Página para login e cadastro de funcionários.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.columnconfigure((0,1), weight=1)

        # Seção de login
        left = StyledLabelFrame(self, text="Logar Funcionário", padx=10, pady=10)
        left.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        left.columnconfigure(0, weight=1)
        for idx, lbl in enumerate(["Matrícula", "Senha"]):
            tk.Label(left, text=lbl, bg=LF_BG, fg=LF_FG).grid(row=idx*2, column=0, sticky="w")
            ent = tk.Entry(left, show='*' if lbl=="Senha" else None)
            ent.grid(row=idx*2+1, column=0, sticky="ew", pady=(0,10))
        tk.Button(
            left,
            text="Logar",
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=PALETTE[4]
        ).grid(row=4, column=0, pady=5)

        # Seção de cadastro de funcionário
        right = StyledLabelFrame(self, text="Cadastrar Funcionário", padx=10, pady=10)
        right.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        right.columnconfigure(0, weight=1)
        for idx, lbl in enumerate(["Nome", "Matrícula", "Senha"]):
            tk.Label(right, text=lbl, bg=LF_BG, fg=LF_FG).grid(row=idx*2, column=0, sticky="w")
            ent = tk.Entry(right, show='*' if lbl=="Senha" else None)
            ent.grid(row=idx*2+1, column=0, sticky="ew", pady=(0,10))
        tk.Button(
            right,
            text="Cadastrar",
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=PALETTE[4]
        ).grid(row=6, column=0, pady=5)


# -------------------------------------------------------------
# Ponto de entrada
# -------------------------------------------------------------
if __name__ == "__main__":
    app = HelpFitApp()
    app.mainloop()
