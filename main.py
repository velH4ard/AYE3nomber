import csv
import os
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox

class RBNode:
    __slots__ = ("key", "ids", "left", "right", "parent", "red")
    def __init__(self, key=None, ids=None, left=None, right=None, parent=None, red=True):
        self.key = key
        self.ids = ids if ids is not None else set()
        self.left = left
        self.right = right
        self.parent = parent
        self.red = red

class RBTree:
    def __init__(self, key_type):
        self.nil = RBNode(red=False)
        self.root = self.nil
        self.key_type = key_type

    def insert(self, key, movie_id):
        if key is None:
            return
        y = self.nil
        x = self.root
        while x is not self.nil:
            y = x
            if key == x.key:
                x.ids.add(movie_id)
                return
            elif key < x.key:
                x = x.left
            else:
                x = x.right
        z = RBNode(key=key, ids={movie_id}, left=self.nil, right=self.nil, parent=y, red=True)
        if y is self.nil:
            self.root = z
        elif key < y.key:
            y.left = z
        else:
            y.right = z
        self._insert_fixup(z)

    def _insert_fixup(self, z):
        while z.parent.red:
            if z.parent is z.parent.parent.left:
                y = z.parent.parent.right
                if y.red:
                    z.parent.red = False
                    y.red = False
                    z.parent.parent.red = True
                    z = z.parent.parent
                else:
                    if z is z.parent.right:
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.red = False
                    z.parent.parent.red = True
                    self._right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left
                if y.red:
                    z.parent.red = False
                    y.red = False
                    z.parent.parent.red = True
                    z = z.parent.parent
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.red = False
                    z.parent.parent.red = True
                    self._left_rotate(z.parent.parent)
        self.root.red = False

    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.nil:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.nil:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, y):
        x = y.left
        y.left = x.right
        if x.right is not self.nil:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is self.nil:
            self.root = x
        elif y is y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x

    def min_node(self, node=None):
        if node is None:
            node = self.root
        if node is self.nil:
            return None
        while node.left is not self.nil:
            node = node.left
        return node

    def successor(self, node):
        if node is None:
            return None
        if node.right is not self.nil:
            return self._min_from(node.right)
        y = node.parent
        while y is not self.nil and node is y.right:
            node = y
            y = y.parent
        return y if y is not self.nil else None

    def _min_from(self, node):
        while node.left is not self.nil:
            node = node.left
        return node

    def find_ge(self, key):
        x = self.root
        res = None
        while x is not self.nil:
            if key == x.key:
                return x
            if key < x.key:
                res = x
                x = x.left
            else:
                x = x.right
        return res

    def range_ids(self, low, high):
        if low is None and high is None:
            node = self.min_node()
        elif low is None:
            node = self.min_node()
        else:
            node = self.find_ge(low)
        if node is None:
            return set()
        out = set()
        while node is not None:
            if high is not None and node.key > high:
                break
            out.update(node.ids)
            node = self.successor(node)
        return out

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None

def parse_float(s):
    if s is None:
        return None
    try:
        return float(s)
    except Exception:
        return None

def load_data(csv_path):
    by_id = {}
    idx_date = RBTree(date)
    idx_vote = RBTree(float)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    with open(csv_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            mid = row.get("id") or row.get("movie_id") or row.get("Id")
            title = row.get("title") or row.get("original_title") or row.get("Title")
            rd = parse_date(row.get("release_date") or row.get("ReleaseDate") or row.get("releaseDate") or row.get("release"))
            va = parse_float(row.get("vote_average") or row.get("VoteAverage") or row.get("rating") or row.get("vote"))
            if not mid:
                continue
            rec = {"id": str(mid), "title": title or "", "release_date": rd, "vote_average": va}
            by_id[str(mid)] = rec
            if rd is not None:
                idx_date.insert(rd, str(mid))
            if va is not None:
                idx_vote.insert(va, str(mid))
    return by_id, idx_date, idx_vote

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Поиск фильмов хоррор")
        self.geometry("900x600")
        try:
            self.by_id, self.idx_date, self.idx_vote = load_data("horror_movies.csv")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить horror_movies.csv: {e}")
            self.destroy()
            return
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(frm, text="Дата релиза от (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W)
        self.e_date_from = ttk.Entry(frm, width=20)
        self.e_date_from.grid(row=0, column=1, padx=5)
        ttk.Label(frm, text="до").grid(row=0, column=2, sticky=tk.W)
        self.e_date_to = ttk.Entry(frm, width=20)
        self.e_date_to.grid(row=0, column=3, padx=5)
        ttk.Label(frm, text="Оценка от").grid(row=1, column=0, sticky=tk.W)
        self.e_vote_from = ttk.Entry(frm, width=20)
        self.e_vote_from.grid(row=1, column=1, padx=5)
        ttk.Label(frm, text="до").grid(row=1, column=2, sticky=tk.W)
        self.e_vote_to = ttk.Entry(frm, width=20)
        self.e_vote_to.grid(row=1, column=3, padx=5)
        self.btn = ttk.Button(frm, text="Искать", command=self._search)
        self.btn.grid(row=0, column=4, rowspan=2, padx=10)
        cols = ("id", "title", "release_date", "vote_average")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, w in zip(cols, (80, 400, 140, 120)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor=tk.W)
        yscroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._populate_all()

    def _populate_all(self):
        self.tree.delete(*self.tree.get_children())
        items = list(self.by_id.values())
        items.sort(key=lambda x: (x["release_date"] or date.min, x["id"]))
        for rec in items:
            rd = rec["release_date"].isoformat() if rec["release_date"] else ""
            va = f"{rec['vote_average']:.1f}" if rec["vote_average"] is not None else ""
            self.tree.insert("", tk.END, values=(rec["id"], rec["title"], rd, va))

    def _search(self):
        df = self.e_date_from.get().strip()
        dt = self.e_date_to.get().strip()
        vf = self.e_vote_from.get().strip()
        vt = self.e_vote_to.get().strip()
        d_low = parse_date(df) if df else None
        d_high = parse_date(dt) if dt else None
        v_low = parse_float(vf) if vf else None
        v_high = parse_float(vt) if vt else None
        ids_date = None
        ids_vote = None
        if d_low is not None or d_high is not None:
            ids_date = self.idx_date.range_ids(d_low, d_high)
        if v_low is not None or v_high is not None:
            ids_vote = self.idx_vote.range_ids(v_low, v_high)
        if ids_date is None and ids_vote is None:
            self._populate_all()
            return
        if ids_date is None:
            ids = ids_vote
        elif ids_vote is None:
            ids = ids_date
        else:
            ids = ids_date & ids_vote
        self.tree.delete(*self.tree.get_children())
        out = []
        for mid in ids:
            rec = self.by_id.get(str(mid))
            if rec:
                out.append(rec)
        out.sort(key=lambda x: (x["release_date"] or date.min, x["id"]))
        for rec in out:
            rd = rec["release_date"].isoformat() if rec["release_date"] else ""
            va = f"{rec['vote_average']:.1f}" if rec["vote_average"] is not None else ""
            self.tree.insert("", tk.END, values=(rec["id"], rec["title"], rd, va))

if __name__ == "__main__":
    App().mainloop()