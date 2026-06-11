import tkinter as tk
from tkinter import ttk
import threading
import re
from resolver import resolve_url


URL_PATTERN = re.compile(r'https?://[^\s<>"\')\]]+')


class App:
    def __init__(self, root):
        root.title("縮短網址還原工具")
        root.geometry("900x620")
        root.resizable(True, True)

        btn_frame = ttk.Frame(root, padding=(10, 5))
        btn_frame.pack(fill=tk.X)
        self.btn = ttk.Button(btn_frame, text="還原", command=self.resolve_all)
        self.btn.pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="清除輸入", command=self.clear_input).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="複製全部結果", command=self.copy_result).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="清除結果", command=self.clear_output).pack(side=tk.LEFT, padx=(10, 0))
        self.status = ttk.Label(btn_frame, text="", foreground="gray")
        self.status.pack(side=tk.RIGHT)

        paned = ttk.PanedWindow(root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        top_frame = ttk.LabelFrame(paned, text="貼上含有縮短網址的內容")
        self.input_text = tk.Text(top_frame, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        paned.add(top_frame, weight=1)

        bottom_frame = ttk.LabelFrame(paned, text="還原結果（可直接複製）")
        self.output_text = tk.Text(bottom_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        paned.add(bottom_frame, weight=1)

    def resolve_all(self):
        content = self.input_text.get("1.0", tk.END).strip()
        if not content:
            return
        urls = list(dict.fromkeys(URL_PATTERN.findall(content)))
        if not urls:
            self.status.config(text="未找到網址")
            return
        self.btn.config(state=tk.DISABLED)
        self.status.config(text=f"正在還原 {len(urls)} 個網址...")

        def run():
            mapping = {}
            done = 0
            for url in urls:
                try:
                    mapping[url] = resolve_url(url)
                except Exception:
                    mapping[url] = url
                done += 1
                self.status.config(text=f"進度: {done}/{len(urls)}")

            result = content
            for short, original in mapping.items():
                result = result.replace(short, original)

            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", result)
            self.output_text.config(state=tk.DISABLED)
            self.status.config(text=f"完成，共替換 {len(urls)} 個網址")
            self.btn.config(state=tk.NORMAL)

        threading.Thread(target=run, daemon=True).start()

    def copy_result(self):
        self.output_text.config(state=tk.NORMAL)
        content = self.output_text.get("1.0", tk.END).strip()
        self.output_text.config(state=tk.DISABLED)
        if not content:
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        self.status.config(text="已複製到剪貼簿")

    def clear_input(self):
        self.input_text.delete("1.0", tk.END)

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
