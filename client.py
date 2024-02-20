import socket 
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import time
import speech as sp

class TicTacToeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe")
        self.window.geometry("1280x760")
        self.window.resizable(False,False)
        self.buttons = []
        self.l = []
        self.nameLabel=tk.Label()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()
        ip=socket.gethostbyname(self.host)
        print(ip)
        self.flag = False
        self.alias = ""
        while True:
            try:
                self.client.connect((ip, 3000))
                break  # Connection successful, exit the loop
            except OSError as e:
                if e.errno == 10035:  # Check for [WinError 10035]
                    # Connection is still in progress, wait and retry
                    time.sleep(1)
                else:
                    # Handle other socket-related errors
                    print(f"Error: {e}")
                    break  # Terminate the loop in case of other errors
        self.opponent=""
        self.create_main_page()

        self.window.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.window.mainloop()

    def clear_placeholder(self, event):
        if self.entry_alias.get() == 'Enter Alias Name':
            self.entry_alias.delete(0, tk.END)

    def restore_placeholder(self, event):
        if not self.entry_alias.get():
            self.entry_alias.insert(0, 'Enter Alias Name')

    #creation of main page
    def create_main_page(self):
        sp.speech("Welcome to the game buddy")
        time.sleep(1)
        self.alias = ""
        data = self.client.recv(1024).decode('utf-8')
        print(json.loads(data))

        self.window.configure(bg='#333333')

        center_frame = tk.Frame(self.window, bg='#A9A9A9')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.entry_alias = tk.Entry(center_frame, width=30, font=('Arial', 16))
        sp.speech("Enter alias name here and press start to start the game")
        self.entry_alias.insert(0, 'Enter Alias Name')
        self.entry_alias.bind("<FocusIn>", self.clear_placeholder)
        self.entry_alias.bind("<FocusOut>", self.restore_placeholder)
        self.entry_alias.pack(pady=20)

        self.start_button = tk.Button(center_frame, text="Start", command=self.alias_enter, bg='#7CFC00', fg='white', font=('Arial', 16), relief=tk.GROOVE)
        self.start_button.pack(pady=10)

        self.window.bind("<Return>", lambda event=None: self.alias_enter())
    def animation(self):
        self.waiting_frame = tk.Frame(self.window, bg='#333333')
        self.waiting_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.waiting_label = tk.Label(self.waiting_frame, text="Waiting for other player to join", font=('Arial', 14), foreground='white', background='#333333')
        self.waiting_label.pack(pady=20)
        self.progressbar = ttk.Progressbar(self.waiting_frame, mode='indeterminate', length=200)
        self.progressbar.pack(pady=10)
        self.progressbar.start()
    
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
            print(response)
            if response['type'] != 'nameError':
                print("creating threads...")
                messagebox.showinfo("Waiting", "waiting for opponent to join")
                self.entry_alias.destroy()
                self.start_button.destroy()

                def process():
                    try:
                        # Set the socket to non-blocking mode
                        self.client.setblocking(0)
                        self.data = b""
                        try:
                            chunk = self.client.recv(1024)
                            if chunk:
                                self.data += chunk
                        except BlockingIOError:
                            pass 
                        if self.data:
                            msg = self.data.decode('utf-8')
                            self.data = json.loads(msg)
                            if self.data['type'] == 'join':
                                print("here",self.data)
                                if self.data['playerSymbol']!="X":
                                    self.flag=True
                                print("opponent is ", self.data['user'])
                                self.opponent += self.data['user']
                                self.window.after(0, self.create_board)
                                self.window.after(0, self.update_board)
                                self.window.after(0, self.client_recieve)
                                self.window.after(0, self.errors)
                                return

                    except Exception as e:
                        print("Something went wrong here... :(  ", str(e))
                    self.window.after(1000,process) 
                self.window.after(0,process)
                self.window.after(0,self.animation)


            else:
                messagebox.showwarning('Same Name', 'Please choose a different name')
                sp.speech("hey buddy u cannt have same name as opponent")
                self.entry_alias.delete(0,tk.END)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
       

#-------------------------------------------------------------------------------------------------------------------------------#
    #playig area
    def create_board(self):
        try:
            print("creating board")
            print("now im here")
            self.progressbar.stop()
            self.waiting_label.destroy()
            self.waiting_frame.destroy()            
        
            print("in after process :)")

            self.alias_label = tk.Label(self.window, text=f'Your Alias: {self.alias}', font=('Arial', 12))
            self.alias_label.grid(row=0, column=1, pady=(0, 10), sticky="nsew")
            self.opponent_label = tk.Label(self.window, text=f'Opponent: {self.opponent}', font=('Arial', 12))
            self.opponent_label.grid(row=4, column=1, rowspan=2, sticky="nsew")
            self.nameLabel=tk.Label(self.window,font=('Arial',21))
            self.nameLabel.grid(row=4,column=2, sticky='nsew')

            for i in range(3):
                row_but = []
                for j in range(3):
                    button = tk.Button(self.window, text="", font=("Arial", 50), anchor="center", height=2, width=6,
                                    bg="lightblue", command=lambda row=i, col=j: self.handle_click(row, col)) #initially set the state as disabled 
                    button.grid(row=i + 1, column=j, sticky="nsew")
                    row_but.append(button)
                self.buttons.append(row_but)
            self.create_chatroom(self.window)
            
            messagebox.showinfo('info', f'You are playing with {self.opponent}')
            exit_button = tk.Button(self.window, text="Exit", command=self.on_exit, bg='#FF0000', fg='white',font=('Arial', 12))
            exit_button.grid(row=6, column=0, pady=10, padx=5, sticky="nsew")
            reset_button = tk.Button(self.window, text="Reset", command=self.reset, bg='#FFD700', fg='black',font=('Arial', 12))
            reset_button.grid(row=6, column=2, pady=10, padx=5, sticky="nsew")


            # Pass the callback function to process
            
        except Exception as e:
            print(f"An error occurred during GUI update: {str(e)}")



    def handle_click(self,row,col):
        if self.client.fileno() == -1:
            print("Socket closed")
            return
        if self.buttons[row][col].cget('state')=='normal' and self.flag:
            d={'type':'move','message':{'row':row,'col':col}}
            json_data=json.dumps(d)
            print(json_data)
            while True:
                self.client.setblocking(0)
                try:
                    self.client.send(json_data.encode('utf-8'))
                    break
                except BlockingIOError:
                    print("Send operation would block. Handle it appropriately.")
                    pass
        
                except Exception as e:
                    print(f"Error occurred during send operation: {e}")
                    pass
            self.l.append([row,col])
            while True:
                self.client.setblocking(0)
                try:
                    data=json.loads(self.client.recv(1024).decode('utf-8'))
                    break
                except BlockingIOError:
                    print("recieve operation would block. Handle it appropriately.")
                    pass
        
                except Exception as e:
                    print(f"Error occurred during recieve operation: {e}")
                    pass  
            #print the server response:
            try:
                print("response:",data)
                if data['type']=='move':
                    if data['playerSymbol']=='X':
                        color='red'
                    else:
                        color='blue'
                    self.buttons[data['row']][data['col']].config(text=data['playerSymbol'], fg=color)
                    for i in range(3):
                        for j in range(3):
                            self.buttons[i][j].config(state='disabled')
                    self.flag=False
                    #disable the button 
                elif data['type']=='gameEnd':
                    if data['winAlias']==self.alias:
                        messagebox.showinfo("Congratulations","You won :)")
                        self.reset_board()
                        print()  
                    elif data['draw']==True:
                        messagebox.showinfo("draw","its a draw.. :)")
                    else:
                        messagebox.showinfo("oops!!   u Lost") 
                        self.reset_board()
                else:
                    self.l.pop()       
            except Exception as e:
                print('Error!',str(e))
                exit(0)
                self.client.close()
        else:
            messagebox.showwarning('warning','sorry pal you cant click this other payer needs to play!') 
            sp.speech("sorry pal you cant click this other payer needs to play")
       


    def update_board(self):
        def process_server_data():
           
           if not self.flag:
            self.nameLabel.config(text="opponents play",fg="blue") 
            try:
                # Set the socket to non-blocking mode
                self.client.setblocking(0)
                data = b""
                try:
                    chunk = self.client.recv(1024)
                    if chunk:
                        data += chunk
                except BlockingIOError:
                    pass  # No data received, continue with non-blocking operations

                if data:
                    message = data.decode('utf-8')
                    data = json.loads(message)
                    print("res in update: ",data)
                    if data['type'] == "move":
                        self.l.append([data['row'],data['col']])
                        for i in range(3):
                            for j in range(3):
                                if [i, j] not in self.l:
                                    self.buttons[i][j].config(state='normal')

                        print("INSIDE UPDATE")
                        if data['playerSymbol'] == 'X':
                            color = 'red'
                        else:
                            color = 'blue'
                        self.buttons[data['row']][data['col']].config(text=data['playerSymbol'], fg=color)
                        self.flag=True
                        self.buttons[data['row']][data['col']].config(state="disabled")
                    elif data['type'] == 'gameEnd':
                        if data['winAlias'] == self.alias:
                            messagebox.showinfo("Congratulations", "You won :)")
                            sp.praise("Congratulations you won")
                            self.reset_board()
                        else:
                            messagebox.showinfo("Oops!!   You Lost")
                            sp.con("Oops you lost it, better luck next time")
                            self.reset_board()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print("Something went wrong:", str(e))
           else:
               self.nameLabel.config(fg="red",text="Your Play")
           self.window.after(100, process_server_data)
        # Initial call to start the loop
        process_server_data()


#-------------------------------------------------------------------------------------------------------------------------------#
    #voice message
    def sendMsg(self,msg):
        self.send_button.config(text="🎤",command=self.voiceMessage)
        print("sending encoded voice message") 
    def voiceMessage(self):
        print("voice message")
        res=messagebox.askyesno("voice","start voice message?")
        if res:
            msg=b""
            self.send_button.config(text="❌",command=self.sendMsg(msg))





        #chat room
    def create_chatroom(self, master):
        chatroom_frame = tk.Frame(master, bg='#115C54')  # Create a frame for the chat room
        chatroom_frame.grid(row=0, column=3, padx=20, rowspan=7, sticky="nsew")  # Adjust column and rowspan as needed

        self.chat_display = tk.Text(chatroom_frame, state='disabled', width=30, height=30, bg='white', font=('Arial', 14))
        self.chat_display.grid(row=0, column=0, padx=15, pady=10, columnspan=5, sticky="nsew")

        self.message_entry = tk.Entry(chatroom_frame, width=40, font=('Arial', 14))
        self.message_entry.insert(0, "Type a message")
        self.message_entry.bind("<FocusIn>", self.on_entry_click)
        self.message_entry.bind("<FocusOut>", self.on_focus_out)
        self.message_entry.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.message_entry.bind("<Return>", self.send_message_enter)

        self.send_button = tk.Button(chatroom_frame, text="➤", command=self.send_message, bg='#3B945E', fg='white', font=('Arial', 14))
        self.send_button.grid(row=4, column=1, padx=10, pady=5, sticky="e")
        self.chat_display.tag_configure('message_box', background='#DCF8C6', foreground='#000000', relief='raised')
        self.chat_display.tag_configure('message_text', foreground='#000000')
        
    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            self.client.send(json.dumps({'type':'chat','message':message}).encode('utf-8'))
            self.chat_display.config(state='normal')
            self.chat_display.tag_configure('right_align', justify='right')
            self.chat_display.insert(tk.END, f"{message}\n", ('right_align',))
            self.chat_display.config(state='disabled')
            self.chat_display.see(tk.END)
            self.message_entry.delete(0, tk.END)


    def send_message_enter(self, event):
        self.send_message()

    def on_entry_click(self, event):
        if self.message_entry.get() == "Type a message":
            self.message_entry.delete(0, "end")
            #delete voice button
            self.send_button.config(command=self.send_message,text="➤")
            self.message_entry.config(fg="black")

    def on_focus_out(self, event):
        if self.message_entry.get() == "":
            self.message_entry.insert(0, "Type a message")
            self.send_button.config(command=self.voiceMessage,text="🎤")
            self.message_entry.config(fg="grey")    

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message)
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)  # Scroll to the bottom


    def client_recieve(self):
        def process_client_receive():
            try:
                self.client.setblocking(0)
                data = b""
                try:
                    chunk = self.client.recv(1024)
                    if chunk:
                        data += chunk
                except BlockingIOError:
                    pass  # No data received, continue with non-blocking operations
                if data:
                    message = data.decode('utf-8')
                    data = json.loads(message)
                    if data['type'] == 'chat':
                        print(data['message'])  # Make it print in chatbot gui
                        self.display_message(f" {data['message']}\n")
            except Exception as e:
                print("Error in client_receive:", str(e))

            # Schedule the function to be called again after 500 milliseconds
            self.window.after(500, process_client_receive)

        process_client_receive()

#-------------------------------------------------------------------------------------------------------------------------------#
    #exit and reset querries
    def on_exit(self):
        result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if result:
            self.client.send(json.dumps({'type': 'exit', 'alias': self.alias}).encode('utf-8'))
            self.window.destroy()
            exit(0)

    def errors(self):
        def process_server_errors():
            try:
                # Set the socket to non-blocking mode
                self.client.setblocking(0)
                data = b""
                try:
                    chunk = self.client.recv(1024)
                    if chunk:
                        data += chunk
                except BlockingIOError:
                    pass  # No data received, continue with non-blocking operations

                if data:
                    # Check if there is data to be received from the server
                    message = data.decode('utf-8')
                    data = json.loads(message)
                    print("In Error section: ",data)
                    if data['type'] == 'exit':
                        messagebox.showinfo('Player Left', 'Opponent left the game')
                    elif data['type'] == 'noPlayer':
                        messagebox.showwarning('Wait Pal', 'Hey buddy, wait for player 2 to join')
                    elif data['type'] == 'restart':
                        res = messagebox.askyesno('Restart', 'Opponent requested a restart. Do you agree?')
                        self.client.send(json.dumps({'type': 'restart', 'val': '1' if res else '0'}).encode('utf-8'))
                    elif data['type'] == "join":
                        messagebox.showinfo('Joined', f'Opponent {data["user"]} joined the game')
                    elif data['type']=="invalidMoveError":
                        messagebox.showerror("error","invalid moove") 
                    elif data['type']=="playerLeft":
                        messagebox.showinfo("playerleft","opponent left the game")      
            except Exception as e:
                print("Something went wrong:", str(e))
            # Schedule the function to be called again after 500 milliseconds
            self.window.after(500, process_server_errors)
        # Initial call to start the loop
        process_server_errors()





    def reset_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state=tk.NORMAL)
        self.l = []

    def reset(self):
        self.client.send(json.dumps({'type':'reset','alias':self.alias}).encode('utf-8'))
       
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
