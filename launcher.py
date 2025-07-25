import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DTE Circulars Launcher")
        self.root.geometry("400x300")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"400x300+{x}+{y}")
    
    def create_widgets(self):
        # Header
        header_label = tk.Label(self.root, text="DTE Karnataka Circulars", 
                               font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        header_label.pack(pady=20)
        
        subtitle_label = tk.Label(self.root, text="Choose your preferred interface", 
                                 font=('Arial', 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack(pady=(0,30))
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(expand=True)
        
        gui_btn = tk.Button(button_frame, text="🖥️ Desktop App\n(Recommended)", 
                           font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                           width=20, height=3, command=self.launch_gui, cursor='hand2')
        gui_btn.pack(pady=10)
        
        web_btn = tk.Button(button_frame, text="🌐 Web App\n(Browser)", 
                           font=('Arial', 12, 'bold'), bg='#3498db', fg='white',
                           width=20, height=3, command=self.launch_web, cursor='hand2')
        web_btn.pack(pady=10)
        
        cli_btn = tk.Button(button_frame, text="💻 Command Line\n(Terminal)", 
                           font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                           width=20, height=3, command=self.launch_cli, cursor='hand2')
        cli_btn.pack(pady=10)
        
        # Footer
        footer_label = tk.Label(self.root, text="Select an option to start scraping DTE circulars", 
                               font=('Arial', 10), fg='#95a5a6', bg='#2c3e50')
        footer_label.pack(side='bottom', pady=10)
    
    def launch_gui(self):
        try:
            subprocess.Popen([sys.executable, 'gui_app.py'])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch GUI app: {str(e)}")
    
    def launch_web(self):
        try:
            subprocess.Popen([sys.executable, 'web_app.py'])
            messagebox.showinfo("Web App Started", 
                              "Web app is starting...\nOpen your browser to: http://localhost:5000")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch web app: {str(e)}")
    
    def launch_cli(self):
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', f'python scraper.py'])
            else:  # Unix/Linux/Mac
                subprocess.Popen(['python', 'scraper.py'])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch CLI app: {str(e)}")

def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()