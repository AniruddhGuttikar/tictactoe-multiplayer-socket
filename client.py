import socket 
import threading
import tkinter as tk
from tkinter import messagebox
import json
import time
import speech as sp

class TicTacToeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe")
        self.buttons = []
        self.l = []

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()
        self.flag = 0
        self.alias = ""
        self.client.connect((self.host, 3000))

        self.create_main_page()

        self.window.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.window.mainloop()
        sp.speech("welcome to the game buddy")

    def clear_placeholder(self, event):
        if self.entry_alias.get() == 'Enter Alias Name':
            self.entry_alias.delete(0, tk.END)

    def restore_placeholder(self, event):
        if not self.entry_alias.get():
            self.entry_alias.insert(0, 'Enter Alias Name')

    #creation of main page
    def create_main_page(self):
        self.alias = ""
        self.client.recv(1024).decode('utf-8')
        self.entry_alias = tk.Entry(self.window, width=30, font=('Arial', 14))
        sp.speech("Enter alais name here and press start to start the game")
        self.entry_alias.insert(0, 'Enter Alias Name')  # Placeholder text
        self.entry_alias.bind("<FocusIn>", self.clear_placeholder)
        self.entry_alias.bind("<FocusOut>", self.restore_placeholder)
        self.entry_alias.pack(pady=50, padx=30)

        start_button = tk.Button(self.window, text="Start", command=self.alias_enter, bg='#7CFC00', fg='white', font=('Arial', 14))
        start_button.pack(pady=10)

    
    def alias_enter(self):
        try:
            self.alias = self.entry_alias.get()
            if self.alias == "" :
                messagebox.showwarning('Empty Alias', 'Please enter an alias.')
                return

            self.client.send(json.dumps({'type': 'alias', 'message': self.alias}).encode('utf-8'))
            print("message sent")
            response = json.loads(self.client.recv(1024).decode('utf-8'))
            print("im here..")
            if response['type'] != 'nameError':
                print("creating threads...")
                create_board_thread = threading.Thread(target=self.create_board)
                update_board_thread = threading.Thread(target=self.update_board)
                client_receive_thread = threading.Thread(target=self.client_recieve)
                errors_thread = threading.Thread(target=self.errors)

                create_board_thread.start()
                update_board_thread.start()
                client_receive_thread.start()
                errors_thread.start()

                create_board_thread.join()
                update_board_thread.join()
                client_receive_thread.join()
                errors_thread.join()

                self.entry_alias.delete(0, tk.END)
                self.start_button.pack_forget()
                self.entry_alias.pack_forget()
            else:
                messagebox.showwarning('Same Name', 'Please choose a different name')
                sp.speech("hey buddy u cannt have same name as opponent")

                self.create_main_page()
        except:
            print("some issue")        

#-------------------------------------------------------------------------------------------------------------------------------#

    #playig area
    def create_board(self):
        self.alias_label = tk.Label(self.window, text=f'Your Alias: {self.alias}', font=('Arial', 12))   #your name 
        self.alias_label.grid(row=0, column=1, pady=(0, 10), sticky="nsew")

        self.opponent_label = tk.Label(self.window, text=f'Opponent: {self.opponent}', font=('Arial', 12))   #name of the opponent
        self.opponent_label.grid(row=4, column=1, pady=(10, 0), sticky="nsew")

        for i in range(3):
            row_but = []
            for j in range(3):
                button = tk.Button(self.window, text="", font=("Arial", 50), anchor="center", height=2, width=6, bg="lightblue", command=lambda row=i, col=j: self.handle_click(row, col))
                button.grid(row=i + 1, column=j, sticky="nsew")
                row_but.append(button)
            self.buttons.append(row_but)
        self.create_chatroom(self.window)    

        opponent = json.loads(self.client.recv(1024).decode('utf-8'))['alias']
        messagebox.showinfo('info', f'You are playing with {opponent}')

        exit_button = tk.Button(self.window, text="Exit", command=self.on_exit, bg='#FF0000', fg='white', font=('Arial', 12))
        exit_button.grid(row=6, column=0, pady=10, padx=5, sticky="nsew")

        reset_button = tk.Button(self.window, text="Reset", command=self.reset, bg='#FFD700', fg='black', font=('Arial', 12))
        reset_button.grid(row=6, column=2, pady=10, padx=5, sticky="nsew")


    def handle_click(self,row,col):
        if self.buttons[row][col]['state']=='normal':
            d={'type:':'game','message':{'row':str(row),'column':str(col)}}
            json_data=json.dumps(d)
            print(json_data)
            self.client.send(json_data.encode('utf-8'))   #json data is passed to the server: (can server know my name???)
            time.sleep(0.2)
            self.l.append([row,col])

            #print the server response:
            try:
                message=self.client.recv(1024).decode('utf-8')
                data=json.loads(message)
                if data['type']=='game':
                    if data['playerSymbol']=='X':
                        color='red'
                    else:
                        color='blue'
                    self.buttons[int(data['row'])][int(data['col'])].config(text=data['playerSymbol'], fg=color)
                    for i in range(3):
                        for j in range(3):
                            self.buttons[i][j]['state'].configure(state='disabled')
                    self.flag+=1
                    #disable the button 
                elif data['type']=='gameEnd':
                    if data['result']==self.alias:
                        messagebox.showinfo("Congradulations","You won :)")
                        time.sleep(2)
                        self.reset_board()
                        print()  
                    else:
                        messagebox.showinfo("oops!!   u Lost") 
                        self.reset_board()
                else:
                    self.fl.pop()       
            except:
                print('Error!')
                self.client.close()
        else:
            messagebox.showwarning('warning','sorry pal you cant click this other payer needs to play!') 
            sp.speech("sorry pal you cant click this other payer needs to play")
       


    def update_board(self):
        while True:
            if self.flag % 2 == 1:
                try:
                    message = self.client.recv(1024).decode('utf-8')
                    for i in range(3):
                        for j in range(3):
                            if [i, j] not in self.l:
                                self.buttons[i][j]['state'].configure(state='normal')
                    data = json.loads(message)
                    if data['type'] == "game":
                        if data['playerSymbol'] == 'X':
                            color = 'red'
                        else:
                            color = 'blue'
                        self.buttons[int(data['row'])][int(data['col'])].config(text=data['playerSymbol'], fg=color)
                        self.flag += 1
                    elif data['type'] == 'gameEnd':
                        if data['result'] == self.alias:
                            messagebox.showinfo("Congratulations", "You won :)")
                            sp.praise("Congradulations you won")
                            self.reset_board()
                        else:
                            messagebox.showinfo("Oops!!   You Lost")
                            sp.con("Oops you lost it better luck next time")
                            self.reset_board()
                except:
                    print("Something went wrong")


#-------------------------------------------------------------------------------------------------------------------------------#


    #chat room
    def create_chatroom(self,master):
        self.master = master
        master.title("Chat Room")
        master.configure(bg='#115C54')  # Set background color
        # Create frame for right half
        self.right_frame = tk.Frame(master, bg='#115C54')
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        # Create text widget for displaying chat messages
        self.chat_display = tk.Text(self.right_frame, state='disabled', width=40, height=20, bg='white')    
        self.chat_display.pack(padx=10, pady=10)
        # Create entry widget for typing messages
        self.message_entry = tk.Entry(self.right_frame, width=40)
        self.message_entry.insert(0, "Type a message")
        self.message_entry.bind("<FocusIn>", self.on_entry_click)
        self.message_entry.bind("<FocusOut>", self.on_focus_out)
        self.message_entry.pack(padx=10, pady=5)
        self.message_entry.bind("<Return>", self.send_message_enter)  # Bind Enter key event
        # Create send button
        self.send_button = tk.Button(self.right_frame, text="Send", command=self.send_message, bg='#3B945E', fg='white')
        self.send_button.pack(side=tk.RIGHT,padx=10, pady=5)
        
    def send_message(self, event=None):  # event argument is for binding to <Button-1>
        message = self.message_entry.get().strip()
        if message:
            self.client.send(json.dumps({'type':'chat','message':message}).encode('utf-8'))
            self.display_message(f"You: {message}\n")
            self.message_entry.delete(0, tk.END)

    def send_message_enter(self, event):
        self.send_message()

    def on_entry_click(self, event):
        if self.message_entry.get() == "Type a message":
            self.message_entry.delete(0, "end")
            self.message_entry.config(fg="black")

    def on_focus_out(self, event):
        if self.message_entry.get() == "":
            self.message_entry.insert(0, "Type a message")
            self.message_entry.config(fg="grey")    

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message)
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)  # Scroll to the bottom


    def client_recieve(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                data = json.loads(message)
                if data['type'] == 'chat':
                    print(data['message'])  # Make it print in chatbot gui
                    self.display_message(f"{data['users']}: {data['message']}\n")
            except:
                print('Error!')
                self.client.close()
                break            

#-------------------------------------------------------------------------------------------------------------------------------#
    #exit and reset querries
    def on_exit(self):
        result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if result:
            self.client.send(json.dumps({'type': 'exit', 'alias': self.alias}).encode('utf-8'))
            self.window.destroy()
            exit(0)

    def errors(self):
        while True:
            try:
                data=json.loads(self.client.recv(1024).decode('utf-8'))
                if(data['type']=='exit'):
                    messagebox.showinfo('player left','opponent left the game')
                elif(data['type']=='noPlayer'):
                    messagebox.showwarning('wait pal, ', 'Hey buddy wait for player2 to join')
                elif(data['type']=='restart'):
                    res=messagebox.askyesno('restart','opponent req for a restart. ')
                    if(res):
                        self.client.send(json.dumps({'type':'restart','val':'1'}).encode('utf-8'))
                    else:
                        self.client.send(json.dumps({'type':'restart','val':'0'}).encode('utf-8'))  
                elif(data['type']=="join"):
                    messagebox.showinfo('joined','opponent '+data['user']+' joined the game')          
            except:
                print("something went wrong")        


    def stop_all_threads(self):
        """Stop all active threads."""
        for thread in threading.enumerate():
            if thread.is_alive():
                thread.join()

    def reset_board(self):
        time.sleep(2)
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state=tk.NORMAL)
        self.l = []

    def reset(self):
        self.client.send(json.dumps({'type':'reset','alias':self.alias}).encode('utf-8'))
        time.sleep(1)
        res = self.client.recv(1024).decode('utf-8')
        data=json.loads(res)
        if(data['val']=='1'):
            for i in range(3):
                for j in range(3):
                    self.buttons[i][j].config(text="", state=tk.NORMAL)
            self.l = []
        else:
            messagebox.showinfo('restart', 'opponent rejected to restart')    
        



if __name__ == "__main__":
    game = TicTacToeGame()
