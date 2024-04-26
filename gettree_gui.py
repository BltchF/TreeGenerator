import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import configparser
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

class TreeGUI:
    def __init__(self, master):
        self.master = master
        master.title("Tree GUI")
        # ========Global Variables================
        # Auto-detect .gitignore file
        self.gitignore_file = self.detect_gitignore()
        # =========Style===========================
        master.configure(bg='black')
        # Define font sizes
        font_size = 16
        smaller_font_size = 12

        # Define styles
        self.style = {'bg': 'black', 'fg': 'white', 'font': ('Helvetica', str(font_size))}
        self.small_button_style = {'bg': 'black', 'fg': 'white', 'font': ('Helvetica', str(smaller_font_size))}

        # Style for text areas
        self.text_area_style = {'bg': '#041726', 'fg': 'white', 'cursor': 'arrow', 'width': font_size}

        # =========================================

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('treeconfig.conf')

        # Row for selecting base directory
        self.base_dir_label = tk.Label(master, text="Base Directory", **self.style)
        self.base_dir_label.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.base_dir_entry = tk.Entry(master, bg='grey', fg='white')
        self.base_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.base_dir_button = tk.Button(master, text="Select", command=self.select_base_dir, **self.style, padx=2, pady=2)
        self.base_dir_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        initial_dir = os.path.dirname(self.gitignore_file) if self.gitignore_file else self.config.get('DEFAULT', 'base_dir', fallback=os.getcwd())
        self.base_dir_entry.insert(0, initial_dir)

        # Display initial directory
        self.initial_dir = self.config.get('DEFAULT', 'base_dir', fallback=os.getcwd())
        self.initial_dir_label = tk.Label(master, text="Initial Directory: " + self.initial_dir, **self.style)
        self.initial_dir_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        # Insert initial directory into base_dir_entry
        self.base_dir_entry.insert(0, initial_dir)

        # Row for selecting .gitignore file
        self.gitignore_label = tk.Label(master, text=".gitignore File", **self.style)
        self.gitignore_label.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        self.gitignore_entry = tk.Entry(master, bg='grey', fg='white')
        self.gitignore_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.gitignore_button = tk.Button(master, text="Select", command=self.select_gitignore, **self.style, padx=2, pady=2)
        self.gitignore_button.grid(row=2, column=2, padx=5, pady=5, sticky='ew')
        self.show_exclusions_button = tk.Button(master, text="Show Exclusions", command=self.show_exclusions, **self.style, padx=2, pady=2)
        self.show_exclusions_button.grid(row=2, column=3, padx=5, pady=5, sticky='ew')
        if self.gitignore_file:
            self.gitignore_entry.insert(0, self.gitignore_file)    

        # Text area for displaying exclusions
        self.exclusions_output = scrolledtext.ScrolledText(master, **self.text_area_style)
        self.exclusions_output.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # Load exclusions from configuration file or .gitignore file
        exclusions = self.config.get('DEFAULT', 'exclusions', fallback=None)
        if exclusions is None and self.gitignore_file:
            with open(self.gitignore_file, 'r') as file:
                exclusions = file.read()
        self.exclusions_output.insert('1.0', exclusions or '')

        # Button for saving exclusions
        self.save_exclusions_button = tk.Button(master, text="Save Exclusions", command=self.save_exclusions, **self.small_button_style, padx=2, pady=2)
        self.save_exclusions_button.grid(row=4, column=0, padx=5, pady=5, sticky='ew')

        # Button for loading exclusions
        self.load_exclusions_button = tk.Button(master, text="Load", command=self.load_exclusions, **self.small_button_style, padx=2, pady=2)
        self.load_exclusions_button.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # Text area for displaying tree output
        self.tree_output = scrolledtext.ScrolledText(master, **self.text_area_style)
        self.tree_output.grid(row=3, column=2, columnspan=2, padx=5, pady=5, sticky='ew')

        # Button for starting generation
        self.start_button = tk.Button(master, text="Start", command=lambda: self.tree_output.insert(tk.END, self.generate_tree()), **self.small_button_style, padx=2, pady=2)
        self.start_button.grid(row=4, column=2, padx=5, pady=5, sticky='ew')

        # Button for copying output
        self.copy_button = tk.Button(master, text="Copy", command=self.copy_output, **self.small_button_style, padx=2, pady=2)
        self.copy_button.grid(row=4, column=3, padx=5, pady=5, sticky='ew')

        
        # Initialize the placement of the window
        self.center_window()

# =================window related function=========================
    def center_window(self):
        self.master.update_idletasks()

        window_width = self.master.winfo_reqwidth()
        window_height = self.master.winfo_reqheight()

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.master.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")


# =================base directory related function=========================
    def select_base_dir(self):
        base_dir = filedialog.askdirectory(initialdir=os.getcwd())
        self.base_dir_entry.delete(0, tk.END)
        self.base_dir_entry.insert(0, base_dir)
        self.store_config()

    def store_config(self):
        self.config['DEFAULT'] = {
            'base_dir': self.base_dir_entry.get(),
            'gitignore': self.gitignore_entry.get()
        }
        with open('treeconfig.conf', 'w') as configfile:
            self.config.write(configfile)

# =================.gitinore related function=========================

    def detect_gitignore(self):
        current_dir = os.getcwd()
        for _ in range(4):
            gitignore_file = os.path.join(current_dir, '.gitignore')
            if os.path.isfile(gitignore_file):
                return gitignore_file
            current_dir = os.path.dirname(current_dir)
        return None

    def select_gitignore(self):
        initial_dir = os.path.dirname(self.gitignore_file) if self.gitignore_file else self.base_dir_entry.get()
        gitignore_file = filedialog.askopenfilename(initialdir=initial_dir, title="Select .gitignore File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        if gitignore_file:
            self.gitignore_entry.delete(0, tk.END)
            self.gitignore_entry.insert(0, gitignore_file)
            with open(gitignore_file, 'r') as file:
                gitignore_contents = file.read()
            self.exclusions_output.delete('1.0', tk.END)
            self.exclusions_output.insert('1.0', gitignore_contents)

    def show_exclusions(self):
        gitignore_file = self.gitignore_entry.get()
        if gitignore_file and os.path.isfile(gitignore_file):
            with open(gitignore_file, 'r') as f:
                exclusions = f.read().splitlines()
            messagebox.showinfo("Exclusions", "\n".join(exclusions))
        else:
            messagebox.showinfo("Exclusions", "No .gitignore file selected")

    def save_exclusions(self):
        exclusions = self.exclusions_output.get('1.0', 'end-1c')
        self.config['DEFAULT']['exclusions'] = exclusions
        self.store_config()

    def load_exclusions(self):
        exclusions = self.config.get('DEFAULT', 'exclusions', fallback='')
        self.exclusions_output.delete('1.0', 'end')
        self.exclusions_output.insert('1.0', exclusions)


# ================= output related function=========================
    def copy_output(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.tree_output.get("1.0", tk.END))

    def generate_tree(self):
        base_dir = self.initial_dir
        gitignore_file = self.gitignore_entry.get()

        if not base_dir:
            return "No base directory selected"

        spec = None
        if gitignore_file:
            with open(gitignore_file, 'r') as f:
                gitignore_patterns = f.read().splitlines()
                spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_patterns)

        tree_output = ""
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if not (spec and spec.match_file(os.path.relpath(os.path.join(root, d) + '/', base_dir)))]
            files = [f for f in files if not (spec and spec.match_file(os.path.relpath(os.path.join(root, f), base_dir)))]

            level = root.replace(base_dir, '').count(os.sep)
            indent = '│   ' * level
            tree_output += '{}├ 📁{}\n'.format(indent, os.path.basename(root))
            subindent = '│   ' * (level + 1)
            for f in files:
                tree_output += '{}├ 📄{}\n'.format(subindent, f)
        return tree_output

if __name__ == "__main__":
    root = tk.Tk()
    gui = TreeGUI(root)
    root.mainloop()