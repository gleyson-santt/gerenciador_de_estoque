import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

conn = sqlite3.connect("estoque.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    validade DATE NOT NULL
)
""")
conn.commit()

def atualizar_lista(mes=None, ano=None):
    for row in tree.get_children():
        tree.delete(row)
    if mes and ano:
        cursor.execute("""
            SELECT id, nome, quantidade, validade FROM produtos
            WHERE strftime('%m', validade)=? AND strftime('%Y', validade)=?
            ORDER BY validade
        """, (f"{int(mes):02d}", str(ano)))
    else:
        cursor.execute("SELECT id, nome, quantidade, validade FROM produtos ORDER BY validade")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def adicionar_produto():
    nome = entry_nome.get().strip()
    quantidade = entry_quantidade.get().strip()
    validade = entry_validade.get().strip()
    if not nome or not quantidade or not validade:
        return messagebox.showwarning("Campos vazios", "Preencha todos os campos.")
    try:
        datetime.strptime(validade, "%Y-%m-%d")
        cursor.execute("INSERT INTO produtos(nome,quantidade,validade) VALUES(?,?,?)",
                       (nome, int(quantidade), validade))
        conn.commit()
        atualizar_lista()
        entry_nome.delete(0, tk.END)
        entry_quantidade.delete(0, tk.END)
        entry_validade.delete(0, tk.END)
        messagebox.showinfo("Sucesso", "Produto adicionado.")
    except ValueError:
        messagebox.showerror("Erro", "Data inválida. Use YYYY-MM-DD.")

def atualizar_quantidade():
    sel = tree.focus()
    novo = entry_nova_qtde.get().strip()
    if not sel:
        return messagebox.showwarning("Selecione", "Selecione um produto.")
    if not novo.isdigit():
        return messagebox.showwarning("Valor inválido", "Quantidade deve ser número.")
    pid = tree.item(sel)["values"][0]
    cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?", (int(novo), pid))
    conn.commit()
    atualizar_lista()
    entry_nova_qtde.delete(0, tk.END)
    messagebox.showinfo("Sucesso", "Quantidade atualizada.")

def remover_vencidos():
    hoje = datetime.today().strftime("%Y-%m-%d")
    cursor.execute("DELETE FROM produtos WHERE validade < ?", (hoje,))
    conn.commit()
    atualizar_lista()
    messagebox.showinfo("Remoção", "Produtos vencidos removidos.")

def filtrar_por_mes():
    m = entry_mes.get().strip()
    a = entry_ano.get().strip()
    if not (m.isdigit() and a.isdigit()):
        return messagebox.showwarning("Entrada inválida", "Mês e ano numéricos.")
    atualizar_lista(m, a)

def editar_produto():
    sel = tree.focus()
    if not sel:
        return messagebox.showwarning("Selecione", "Selecione um produto.")
    pid, n0, q0, v0 = tree.item(sel)["values"]

    edit = tk.Toplevel(root)
    edit.title("Editar Produto")
    edit.configure(bg="white")
    edit.geometry("380x230")
    edit.grab_set()

    ttk.Label(edit, text="Nome:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
    e_nome = ttk.Entry(edit, width=30)
    e_nome.insert(0, n0)
    e_nome.grid(row=0, column=1, pady=8)

    ttk.Label(edit, text="Quantidade:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
    e_q = ttk.Entry(edit, width=10)
    e_q.insert(0, q0)
    e_q.grid(row=1, column=1, pady=8, sticky="w")

    ttk.Label(edit, text="Validade (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=8, sticky="w")
    e_v = ttk.Entry(edit, width=20)
    e_v.insert(0, v0)
    e_v.grid(row=2, column=1, pady=8, sticky="w")

    def salvar():
        nn, nq, nv = e_nome.get().strip(), e_q.get().strip(), e_v.get().strip()
        if not nn or not nq or not nv:
            return messagebox.showwarning("Campos vazios", "Preencha todos os campos.")
        try:
            nq = int(nq)
            datetime.strptime(nv, "%Y-%m-%d")
            cursor.execute("UPDATE produtos SET nome=?,quantidade=?,validade=? WHERE id=?",
                           (nn, nq, nv, pid))
            conn.commit()
            atualizar_lista()
            messagebox.showinfo("Sucesso", "Produto atualizado.")
            edit.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Verifique os dados.")

    def excluir():
        if messagebox.askyesno("Confirmar", "Excluir este produto?"):
            cursor.execute("DELETE FROM produtos WHERE id=?", (pid,))
            conn.commit()
            atualizar_lista()
            messagebox.showinfo("Removido", "Produto excluído.")
            edit.destroy()

    fb = ttk.Frame(edit)
    fb.grid(row=3, column=0, columnspan=2, pady=15)
    ttk.Button(fb, text="Salvar", command=salvar).grid(row=0, column=0, padx=8)
    rb = ttk.Button(fb, text="Excluir", command=excluir)
    rb.grid(row=0, column=1, padx=8)
    rb.configure(style="Danger.TButton")

root = tk.Tk()
root.title("Gerenciador de Estoque")
root.geometry("960x620")
root.configure(bg="white")

style = ttk.Style()
style.theme_use("alt")
style.configure("Treeview", font=("Segoe UI",10), rowheight=26,
                background="white", fieldbackground="white", borderwidth=0)
style.configure("Treeview.Heading", background="#f0f0f0", foreground="#333",
                font=("Segoe UI",10,"bold"), relief="flat")
style.map("Treeview", background=[("selected", "#cce6ff")])
style.configure("TLabel", background="white", font=("Segoe UI",10))
style.configure("TEntry", font=("Segoe UI",10), padding=5)
style.configure("TButton", font=("Segoe UI",10), padding=6, relief="flat",
                background="#e6f2ff")
style.map("TButton", background=[("active", "#cce6ff")])
style.configure("Danger.TButton", foreground="#800000", background="#ffe6e6")
style.map("Danger.TButton", background=[("active", "#ffcccc")])

f_top = ttk.Frame(root, padding=10)
f_top.pack(pady=10)
f_table = ttk.Frame(root, padding=10)
f_table.pack(padx=20, pady=10, fill="both", expand=True)
f_bot = ttk.Frame(root, padding=10)
f_bot.pack(pady=10)

ttk.Label(f_top, text="Produto:").grid(row=0, column=0, padx=5, pady=5)
entry_nome = ttk.Entry(f_top, width=30)
entry_nome.grid(row=0, column=1, padx=5)
ttk.Label(f_top, text="Quantidade:").grid(row=0, column=2, padx=5)
entry_quantidade = ttk.Entry(f_top, width=10)
entry_quantidade.grid(row=0, column=3, padx=5)
ttk.Label(f_top, text="Validade:").grid(row=0, column=4, padx=5)
entry_validade = ttk.Entry(f_top, width=15)
entry_validade.grid(row=0, column=5, padx=5)
ttk.Button(f_top, text="Adicionar Produto", command=adicionar_produto).grid(row=0, column=6, padx=10)

cols = ("ID","Nome","Quantidade","Validade")
tree = ttk.Treeview(f_table, columns=cols, show="headings", height=12)
for c in cols:
    tree.heading(c,text=c)
    tree.column(c,anchor="center",width=150)
tree.pack(fill="both",expand=True)

sbar = ttk.Scrollbar(f_table, orient="vertical", command=tree.yview)
tree.configure(yscroll=sbar.set)
sbar.pack(side="right",fill="y")

ttk.Label(f_bot, text="Nova Qtde:").grid(row=0, column=0, padx=5)
entry_nova_qtde = ttk.Entry(f_bot, width=10)
entry_nova_qtde.grid(row=0, column=1)
ttk.Button(f_bot, text="Atualizar Qtde", command=atualizar_quantidade).grid(row=0, column=2, padx=10)
ttk.Label(f_bot, text="Mês:").grid(row=1, column=0, padx=5)
entry_mes = ttk.Entry(f_bot, width=5)
entry_mes.grid(row=1, column=1)
ttk.Label(f_bot, text="Ano:").grid(row=1, column=2, padx=5)
entry_ano = ttk.Entry(f_bot, width=7)
entry_ano.grid(row=1, column=3)
ttk.Button(f_bot, text="Filtrar", command=filtrar_por_mes).grid(row=1, column=4, padx=10)
ttk.Button(f_bot, text="Limpar Filtro", command=lambda: atualizar_lista()).grid(row=1, column=5, padx=10)
ttk.Button(f_bot, text="Editar Produto", command=editar_produto).grid(row=2, column=0, pady=15, sticky="w", padx=5)
ttk.Button(f_bot, text="Remover Vencidos", command=remover_vencidos).grid(row=2, column=1, columnspan=5, pady=15)

atualizar_lista()
root.mainloop()
conn.close()
