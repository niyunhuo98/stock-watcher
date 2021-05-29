import bs4, requests, threading, datetime
import tkinter as tk
from tkmacosx import Button
from tkinter import messagebox
from functools import partial


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stock Watcher")
        self.geometry("600x600+0+0")

        self.search_frame = tk.Frame(self, width=600, height=50)
        self.label = tk.Label(self.search_frame, text="Stock Ticker:")
        self.entry = tk.Entry(self.search_frame, width=25)
        self.entry.focus()
        self.entry.bind("<Return>", self.add_stock)
        self.button = Button(self.search_frame, text="Add Ticket", bg="blue", fg="white", command=self.add_stock)
        self.time = tk.Label(self.search_frame, fg="red", font=(None, '14', 'bold'))

        self.stocks_frame = tk.Frame(self, width=600, height=550)
        self.stocks_d = {}
        self.row = 0
        self.display()
        self.update_time()

    
    def display(self):
        self.search_frame.pack()
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT)
        self.button.pack(side=tk.LEFT)
        self.time.pack(side=tk.LEFT)
        self.stocks_frame.pack()
    

    def update_time(self):
        self.time.config(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.time.after(200, self.update_time)

    
    def add_stock(self, arg=None):
        try:
            (self.price, self.change) = self.get_price(self.entry.get())
        except IndexError:
            messagebox.showinfo("Error", "Stock not found")
            self.entry.delete(0, tk.END)
        else:
            if not self.change or not self.price:
                messagebox.showinfo("Error", "Stock not found")
            elif self.entry.get().upper() not in self.stocks_d:
                self.stocks_d[self.entry.get().upper()] = [tk.Label(self.stocks_frame, text=self.entry.get().upper(), font=(None, '14', 'bold'))]
                self.stocks_d[self.entry.get().upper()].append(tk.Label(self.stocks_frame, text=self.price, font=(None, '14', 'bold')))
                if self.change[0] == '-':
                    self.stocks_d[self.entry.get().upper()].append(tk.Label(self.stocks_frame, text=self.change, font=(None, '14', 'bold'), fg="red"))
                elif self.change[1] == '+':
                    self.stocks_d[self.entry.get().upper()].append(tk.Label(self.stocks_frame, text=self.change, font=(None, '14', 'bold'), fg="green"))
                else:
                    self.stocks_d[self.entry.get().upper()].append(tk.Label(self.stocks_frame, text=self.change, font=(None, '14', 'bold'), fg="black"))
                self.stocks_d[self.entry.get().upper()].append(Button(self.stocks_frame, text="Remove", bg="red", fg="white", command=partial(self.remove_stock, self.stocks_d[self.entry.get().upper()][0]['text'])))
                self.stocks_d[self.entry.get().upper()][0].grid(row=self.row)
                self.stocks_d[self.entry.get().upper()][1].grid(row=self.row, column=1)
                self.stocks_d[self.entry.get().upper()][2].grid(row=self.row, column=2)
                self.stocks_d[self.entry.get().upper()][3].grid(row=self.row, column=3)
                self.row+=1
                threading._start_new_thread(self.update_price, (self.entry.get().upper(),))
            else:
                messagebox.showinfo("Error", "Already added to watchlist")
            self.entry.delete(0, tk.END)
    

    def get_price(self, name):
        self.res = requests.get('https://finance.yahoo.com/quote/'+name)
        self.res.raise_for_status()
        self.soup = bs4.BeautifulSoup(self.res.text, 'html.parser')
        self.price = self.soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
        self.change = self.soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find_all('span')[1].text
        return (self.price, self.change)


    def update_price(self, name):
        while True:
            (self.price, self.change) = self.get_price(name)
            try:
                self.stocks_d[name][1].config(text=self.price)
                if not self.price or not self.change:
                    pass
                elif self.change[0] == "-":
                    self.stocks_d[name][2].config(text=self.change, fg="red")
                elif self.change[0] == "+":
                    self.stocks_d[name][2].config(text=self.change, fg="green")
                else:
                    self.stocks_d[name][2].config(text=self.change, fg="black")
            except KeyError:
                break

    
    def remove_stock(self, name):
        self.stocks_d[name][0].destroy()
        self.stocks_d[name][1].destroy()
        self.stocks_d[name][2].destroy()
        self.stocks_d[name][3].destroy()
        del self.stocks_d[name]


if __name__ == "__main__":
    root = MainApp()
    root.mainloop()