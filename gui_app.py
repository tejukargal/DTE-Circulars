import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import webbrowser
from scraper import DTECircularScraper
import json
from datetime import datetime

class DTECircularsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DTE Karnataka Circulars")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.scraper = DTECircularScraper()
        self.circulars = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=10, pady=(10,0))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="DTE Karnataka Circulars", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(header_frame, text="Latest Government Orders, Circulars & Notices", 
                                 font=('Arial', 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # Controls
        controls_frame = tk.Frame(self.root, bg='#f0f0f0')
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        self.refresh_btn = tk.Button(controls_frame, text="🔄 Refresh Circulars", 
                                    font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                    command=self.refresh_circulars, cursor='hand2')
        self.refresh_btn.pack(side='left', padx=(0,10))
        
        self.export_btn = tk.Button(controls_frame, text="💾 Export to JSON", 
                                   font=('Arial', 12), bg='#3498db', fg='white',
                                   command=self.export_json, cursor='hand2')
        self.export_btn.pack(side='left', padx=(0,10))
        
        self.status_label = tk.Label(controls_frame, text="Ready", 
                                    font=('Arial', 10), fg='#7f8c8d', bg='#f0f0f0')
        self.status_label.pack(side='right')
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=(0,10))
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        
        # Circulars list with scrollbar
        list_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        list_frame.pack(fill='both', expand=True)
        
        # Scrollable text widget
        self.text_widget = scrolledtext.ScrolledText(list_frame, wrap=tk.WORD, 
                                                    font=('Segoe UI', 10), bg='white',
                                                    padx=15, pady=15)
        self.text_widget.pack(fill='both', expand=True)
        
        # Configure text tags for styling
        self.text_widget.tag_configure('title', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        self.text_widget.tag_configure('date', font=('Arial', 10), foreground='#27ae60')
        self.text_widget.tag_configure('order', font=('Arial', 10), foreground='#8e44ad')
        self.text_widget.tag_configure('description', font=('Arial', 10), foreground='#34495e')
        self.text_widget.tag_configure('link', font=('Arial', 10, 'underline'), foreground='#3498db')
        self.text_widget.tag_configure('separator', font=('Arial', 8), foreground='#bdc3c7')
        
        # Bind click events for links
        self.text_widget.tag_bind('link', '<Button-1>', self.open_link)
        self.text_widget.tag_bind('link', '<Enter>', lambda e: self.text_widget.configure(cursor='hand2'))
        self.text_widget.tag_bind('link', '<Leave>', lambda e: self.text_widget.configure(cursor=''))
        
        # Load initial data
        self.refresh_circulars()
        
    def refresh_circulars(self):
        def fetch_data():
            try:
                self.progress.start()
                self.refresh_btn.configure(state='disabled')
                self.status_label.configure(text="Fetching circulars...")
                
                self.circulars = self.scraper.scrape_circulars()
                
                self.root.after(0, self.display_circulars)
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error fetching circulars: {str(e)}"))
            finally:
                self.root.after(0, self.fetch_complete)
        
        thread = threading.Thread(target=fetch_data)
        thread.daemon = True
        thread.start()
    
    def fetch_complete(self):
        self.progress.stop()
        self.refresh_btn.configure(state='normal')
        self.status_label.configure(text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def display_circulars(self):
        self.text_widget.delete(1.0, tk.END)
        
        if not self.circulars:
            self.text_widget.insert(tk.END, "No circulars found.\n\n")
            self.text_widget.insert(tk.END, "The website might be temporarily unavailable or the structure may have changed.")
            return
        
        self.text_widget.insert(tk.END, f"📋 Found {len(self.circulars)} Recent Circulars\n\n", 'title')
        
        for i, circular in enumerate(self.circulars, 1):
            # Title
            self.text_widget.insert(tk.END, f"{i}. ", 'title')
            self.text_widget.insert(tk.END, f"{circular['title']}\n", 'title')
            
            # Date and Order
            self.text_widget.insert(tk.END, f"📅 Date: ", 'date')
            self.text_widget.insert(tk.END, f"{circular['date']}\n", 'date')
            
            if circular.get('order_number'):
                self.text_widget.insert(tk.END, f"📋 Order: ", 'order')
                self.text_widget.insert(tk.END, f"{circular['order_number']}\n", 'order')
            
            # Description
            self.text_widget.insert(tk.END, f"📄 Description: ", 'description')
            self.text_widget.insert(tk.END, f"{circular['description']}\n", 'description')
            
            # Link
            if circular.get('link'):
                self.text_widget.insert(tk.END, f"🔗 View Document: ", 'description')
                link_start = self.text_widget.index(tk.INSERT)
                self.text_widget.insert(tk.END, circular['link'], 'link')
                link_end = self.text_widget.index(tk.INSERT)
                
                # Store link for click handling
                self.text_widget.tag_add(f'link_{i}', link_start, link_end)
                self.text_widget.tag_bind(f'link_{i}', '<Button-1>', 
                                        lambda e, url=circular['link']: self.open_url(url))
                self.text_widget.insert(tk.END, "\n")
            
            # Separator
            self.text_widget.insert(tk.END, "─" * 80 + "\n\n", 'separator')
    
    def open_link(self, event):
        pass  # Handled by individual link tags
    
    def open_url(self, url):
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open URL: {str(e)}")
    
    def export_json(self):
        if not self.circulars:
            messagebox.showwarning("No Data", "No circulars to export. Please refresh first.")
            return
        
        try:
            filename = f"circulars_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.circulars, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Export Successful", f"Circulars exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export data: {str(e)}")
    
    def show_error(self, error_msg):
        messagebox.showerror("Error", error_msg)
        self.status_label.configure(text="Error occurred")

def main():
    root = tk.Tk()
    app = DTECircularsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()