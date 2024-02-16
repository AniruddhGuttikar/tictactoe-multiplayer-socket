import socket 
import threading
import tkinter as tk
from tkinter import messagebox
import json
import time

window = tk.Tk()
window.title("Tic Tac Toe")
buttons=[]
l=[]
# Create board
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host=socket.gethostname()
print(socket.gethostbyname(host))
flag=0
alias=""
#connect client to server here
client.connect((host,3000))


#create a function asking for alias name enter
#inside that initialise thread and everything use class

def reset_board():
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text="", state=tk.NORMAL)
    l=[]        

def handle_click(row,col):
    if buttons[row][col]['state']=='normal':
        d={'type:':'game','message':{'row':str(row),'column':str(col)}}
        json_data=json.dumps(d)
        print(json_data)
        client.send(json_data.encode('utf-8'))   #json data is passed to the server: (can server know my name???)
        time.sleep(0.2)
        l.append([row,col])

        #print the server response:
        try:
            message=client.recv(1024).decode('utf-8')
            data=json.loads(message)
            if data['type']=='game':
                if data['playerSymbol']=='X':
                    color='red'
                else:
                    color='blue'
                buttons[int(data['row'])][int(data['col'])].config(text=data['playerSymbol'], fg=color)
                for i in range(3):
                    for j in range(3):
                        buttons[i][j]['state'].configure(state='disabled')
                flag+=1
                #disable the button 
            elif data['type']=='gameEnd':
                if data['result']==alias:
                    messagebox.showinfo("Congradulations","You won :)")
                    reset_board()
                    print()  
                else:
                    messagebox.showinfo("oops!!   u Lost") 
                    reset_board()
        except:
            print('Error!')
            client.close()
    else:
        messagebox.showwarning('warning','sorry pal you cant click this other payer needs to play!')        
    

def create_board():
    for i in range(3):
        row_but=[]
        for j in range(3):
           
            button = tk.Button(window, text="", font=("Arial", 50), anchor="center",  height=2, width=6, bg="lightblue", command=lambda row=i, col=j: handle_click(row, col))
            button.grid(row=i, column=j, sticky="nsew")
            row_but.append(button)
        buttons.append(row_but)
    opponent=json.loads(client.recv(1024).decode('utf-8'))['alias']
    messagebox.showinfo('info',f'you are playing with ${opponent}')

def update_board():
    while True:
        if flag%2 ==1:
            try:
                message=client.recv(1024).decode('utf-8')
                #here try to updae so that client2 responce is taken...
                for i in range(3):
                    for j in range(3):
                        if [i,j] not in l:
                            buttons[i][j]['state'].configure(state='normal')
                data=json.loads(message)
                if data['type']=="game":
                    if data['playerSymbol']=='X':
                        color='red'
                    else:
                        color='blue'

                    buttons[int(data['row'])][int(data['col'])].config(text=data['playerSymbol'], fg=color)
                    flag+=1                #disable the button 
                elif data['type']=='gameEnd':
                    if data['result']==alias:
                        messagebox.showinfo("Congradulations","You won :)")
                        reset_board()
                        print()  
                    else:
                        messagebox.showinfo("oops!!   u Lost") 
                        reset_board()
            except:
                print("something went wrong")    


#hetr do the ssme for char room
def client_recieve():
    while True:
        try:
            message=client.recv(1024).decode('utf-8')
            data=json.loads(message)
            if data['type']=='alias':
                client.send(json.dumps({'type':'alias','message':alias}).encode('utf-8'))
            elif data['type'=='chat']:
                print(data['message'])  #make it print in chatbot gui
        except:
            print('Error!')
            client.close()
            break

def client_send():
    while True:
        message=f'{alias}: {input("")}'   #take the input from textbox of chat gui

        client.send(json.encode('utf-8'))
def restart():
    messagebox.showwarning('confirm to restart')

def errors():
    while True:
        try:
            data=json.loads(client.recv(1024).decode('utf-8'))
            if(data['type']=='exit'):
                messagebox.showinfo('player left','opponent left the game')
            elif(data['type']=='noPlayer'):
                messagebox.showwarning('wait pal, ', 'Hey buddy wait for player2 to join')

        except:
            print()
        
def alias_enter():
    global alias
  #input alias name from a label and send it to server
    while True:
        if(alias==""):
            alias=input("alais:>>")
            #input alias name in gui
            client.send(json.dumps({'type':'alias','name':alias}).encode('utf-8'))
            if(json.loads(client.recv(1024).decode('utf-8'))['ok']=='1'):
                    threading.Thread(target=create_board).start()
                    threading.Thread(target=update_board).start()
                    threading.Thread(target=client_recieve).start()
                    threading.Thread(target=client_send).start()
            else:
                messagebox.showwarning('same name','same name plz choose some other name')

def stop_all_threads():
    """Stop all active threads."""
    for thread in threading.enumerate():
        if thread.is_alive():
            thread.join()
          
def on_exit():
    result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
    if result:
        client.send(json.dumps({'type':'exit','alias':alias}).encode('utf-8'))
        #if required print exiting in 3 2 1 then exit
        window.destroy()
        exit(0)

def mainpage():
  alias=""
  #cre	te gui for start button and call alias_enter function
  #stop_all_threads()
  #ask here to enter the alias
  alias_enter()

mainpage()
                      


window.protocol("WM_DELETE_WINDOW", on_exit)


window.mainloop()
''' todo list:
1.create a a reset button that resets the page
2.create a exit button when clicked call a function which removes all thread and caals mainpage()'''
