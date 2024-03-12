import socket 
import tkinter as tk
from threading import Thread
from tkinter import ttk
from tkinter import messagebox
import json
import time
import speech as sp
from ttkthemes import ThemedStyle
import pygame
import speech_recognition as sr
import cv2
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip
import pynput
import emoji
import platform


class FullscreenVideo(tk.Label):
    def __init__(self, master=None, video_path="", duration=7, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.configure(bg='black')  # Set background color to black for better visibility
        self.place(relwidth=1, relheight=1)
        self.configure(cursor="none")
        # Load the video clip
        video_clip = VideoFileClip(video_path)

        # Set up the Tkinter window
        self.master = master
        self.master.attributes("-fullscreen", True)

        # Play the video with audio for the specified duration
        self.video_label = tk.Label(self)
        self.video_label.place(relwidth=1, relheight=1)
        self.video_label.bind("<Escape>", self.quit_fullscreen)
        self.video_clip = video_clip
        self.video_label.after(duration * 1000, self.quit_fullscreen)  # Set a timer for video duration
        self.play_video()

    def play_video(self):
        self.video_clip.preview()

    def quit_fullscreen(self, event=None):
        self.video_clip.close()

        # Undisplay (unmount) everything created by this class
        self.video_label.place_forget()
        self.place_forget()


class FullscreenVideoLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.configure(bg='black')  # Set background color to black for better visibility
        self.place(relwidth=1, relheight=1)
        self.configure(cursor="none")


class TicTacToeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe")
        self.window.geometry("1280x760")
        self.window.resizable(False,False)
        self.game_started=False
        self.buttons = []
        self.chat_display=tk.Text()
        self.window.configure(bg='#333333')
        self.path_to_server = ".\\server\\server.js"
        self.l = []
        self.ip_list=[]
        self.mySymbol=""
        self.gameroom=""
        self.nameLabel=tk.Label()
        self.host = socket.gethostname() 
        self.ip_current=socket.gethostbyname(self.host)
        print(self.ip_current)
        self.flag = False
        self.alias = ""
        self.opponent=""
        # self.initialize_emoji_data()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_list=[]
        self.host=""
        self.window.after(0,self.joinMainServer)
        self.window.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.server_process=None
        self.thread=None
        self.window.bind('<Motion>', self.on_motion)
        self.window.bind('<Key>', self.on_key_press)
        self.afk_threshold = 5
        self.last_activity_time = time.time()
        self.video_file_path = "client/vedio.mp4"
        self.video_label = None
        self.video_thread_running = False




        #self.music_thread = Thread(target=self.play_music)
        # self.music_thread.start()
        # self._stop_event=threading.Event()
        pygame.mixer.init()
        pygame.mixer.music.load('client/song.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()



        self.id=""
        self.dataDict={}
        self.window.mainloop()



    def on_motion(self, event):
        self.last_activity_time = time.time()

    def on_key_press(self, event):
        self.last_activity_time = time.time()

    def check_afk_status(self):
        elapsed_time = time.time() - self.last_activity_time
        if elapsed_time > self.afk_threshold:
            self.play_video()
        else:
            self.stop_video()
        self.window.after(10, self.check_afk_status)

    def play_video(self):
        if self.video_label is None:
            self.container = tk.Frame(self.window)
            self.container.place(relwidth=1, relheight=1)
            self.video_label = FullscreenVideoLabel(self.container)

        if not self.video_thread_running:
            self.video_thread_running = True
            self.video_thread = Thread(target=self._play_video_thread)
            self.video_thread.start()

    def _play_video_thread(self):
        cap = cv2.VideoCapture(self.video_file_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Failed to open the video file.")
            self.video_thread_running = False
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = cv2.resize(rgb_frame, (640, 480))
            image = Image.fromarray(rgb_frame)
            photo_image = ImageTk.PhotoImage(image=image)

            if self.video_label != None:
                self.video_label.config(image=photo_image)
                self.video_label.image = photo_image

            if not self.window.winfo_exists():
                break

            if time.time() - self.last_activity_time < self.afk_threshold:
                break

        cap.release()
        self.video_thread_running = False
        self.window.after(100, self.clear_video_label)

    def stop_video(self):
        if self.video_thread_running:
            self.video_thread_running = False
            self.window.after(100, self.clear_video_label)

    def clear_video_label(self):
        if self.video_label is not None:
            self.video_label.destroy()
            self.container.destroy()
            self.video_label = None        

    def main(self):
        
        self.window.after(0,self.check_afk_status())
        self.waiting_frame.destroy()
        self.progressbar.destroy()
        self.waiting_label.destroy() 
        self.center_frame = tk.Frame(self.window, bg='#A9A9A9')
        self.center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.host_button = tk.Button(self.center_frame, text="Host a Game", bg='blue', fg='white', font=('Arial', 14), command=self.hostname)
        self.host_button.grid(row=0, column=0, padx=10, pady=10)
        self.join_button = tk.Button(self.center_frame, text="Join a Game", bg='orange', fg='white', font=('Arial', 14), command=self.joinGame)
        self.join_button.grid(row=0, column=1, padx=10, pady=10)
        self.back_button = tk.Button(self.window, text="Back", command=self.goBack, bg='#FF4500', fg='white', font=('Arial', 14))
        self.back_button.place(x=10, y=10)
        self.host_button.bind("<Enter>", lambda event, button=self.host_button: self.onEnter(event, button))
        self.host_button.bind("<Leave>", lambda event, button=self.host_button: self.onLeave(event, button))
        self.join_button.bind("<Enter>", lambda event, button=self.join_button: self.onEnter(event, button))
        self.join_button.bind("<Leave>", lambda event, button=self.join_button: self.onLeave(event, button))

        

    def animation3(self):
        self.waiting_frame = tk.Frame(self.window, bg='#333333')
        self.waiting_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.waiting_label = tk.Label(self.waiting_frame, text="connectiong to server", font=('Arial', 14), foreground='white', background='#333333')
        self.waiting_label.pack(pady=20)
        self.progressbar = ttk.Progressbar(self.waiting_frame, mode='indeterminate', length=200)
        self.progressbar.pack(pady=10)
        self.progressbar.start()         

    def joinMainServer(self):
        print("hello man")
        #hostnames=gi.gethostname()
        self.window.after(0,self.animation3)
        try:
            #self.client.connect((i[1],3000))
            self.client.connect(("192.168.0.111",3000))
            #FullscreenVideo(self.window, video_path=self.video_file_path)
            pygame.mixer.init()
            pygame.mixer.music.load('client\song.mp3')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play()
            self.window.after(0,self.main)
        except Exception as e:
            print("unable to connect to main server retrying!!!")
            self.window.after(0,self.joinMainServer)  
                   

    def hostname(self):
        try:
            self.center_frame.destroy()
            self.host_button.destroy()
            self.join_button.destroy()
            self.host = ""
            time.sleep(1)
            self.window.configure(bg='#333333')
            center_frame = tk.Frame(self.window, bg='#A9A9A9')
            center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.entry_hostname = tk.Entry(center_frame, width=30, font=('Arial', 16))
            sp.speech("ENTER THEE HOSTNAME")
            self.entry_hostname.insert(0, 'Enter HOST Name')
            self.entry_hostname.bind("<FocusIn>", self.clear_placeholder_host)
            self.entry_hostname.bind("<FocusOut>", self.restore_placeholder_host)
            self.entry_hostname.pack(pady=20)
            self.start_button = tk.Button(center_frame, text="Start", command=self.hostname_enter, bg='#7CFC00', fg='white', font=('Arial', 16), relief=tk.GROOVE)
            self.start_button.pack(pady=10)
            self.window.bind("<Return>", lambda event=None: self.hostname_enter())
        except Exception as e:
            print("error occured: ",str(e))   
    def clear_placeholder_host(self, event):
        if self.entry_hostname.get() == 'Enter HOST Name':
            self.entry_hostname.delete(0, tk.END)
    def restore_placeholder_host(self, event):
        if not self.entry_hostname.get():
            self.entry_hostname.insert(0, 'Enter HOST Name')                

    def start_countdown(self, seconds):
        for i in range(seconds, 0, -1):
            self.countdown_label.config(text=str(i))
            time.sleep(1)
        self.countdown_label.config(text="Go!!", foreground="green")
        self.window.after(1000, self.clear_label)

    def clear_label(self):
        self.countdown_label.config(text="")
        self.window.after(1000, self.show_game_start)
    def stop(self):
        self._stop_event.set()
    def game(self):
        # self.th._stop()
        # self.th.join()   
        self.countdown_label.destroy()
        self.window.after(0, self.create_main_page)

    def show_game_start(self):
        game_start_label = ttk.Label(self.window, text="Game Starts!", font=("Helvetica", 30, "bold"), foreground="blue")
        game_start_label.pack(expand=True)
        self.window.after(3000, lambda: game_start_label.pack_forget())  # Display for 3 seconds
        self.window.after(4000, self.game)  # Close the window after 4 seconds

    def hostname_enter(self):
        try:
            self.host = self.entry_hostname.get()
            if self.host == "":
                messagebox.showwarning('Empty hostname', 'Please enter a hostname.')
                return

            # This sends and links with the 2nd client
            self.client.send(json.dumps({'type': 'createGame', 'message': self.host}).encode('utf-8'))
            print("message sent")
            self.data = b""
            def pro():
                self.data = b""
                self.client.setblocking(0)
                try:
                    chunk = self.client.recv(1024)
                    if chunk:
                        self.data += chunk
                except BlockingIOError:
                    pass 
                if self.data:
                    print("returning data: in hostname enter: ",self.data)
                    response=json.loads(self.data.decode('utf-8'))
                    print("im here..")
                    print(response)
                    if response['type'] != 'nameError':
                        self.entry_hostname.destroy()
                        self.start_button.destroy()
                        self.style = ThemedStyle(self.window)
                        self.style.set_theme("plastik")  # You can try different themes
                        self.countdown_label = ttk.Label(self.window, text="", font=("Helvetica", 50, "bold"), foreground="red")
                        self.countdown_label.pack(expand=True)
                        self.gameroom+=self.host
                        self.start_countdown(3)
                        # Hostname agreed
                    else:
                        messagebox.showwarning('Same Name', 'Please choose a different name')
                        self.entry_hostname.delete(0, tk.END)
                else:  
                    self.window.after(100,pro)
            if pro()==None:
                return
        except Exception as e:
            print(f"An error occurred in hostname enter: {str(e)}")


#*--------------------------------------------------------------------------------------------------------------------------------------------------------------
            

    def joinGame(self):
        #request from client 2 to give all hostnames with ip
        try:    
            self.client.send(json.dumps({'type':'joinGame'}).encode('utf-8'))
            self.center_frame.destroy()
            self.host_button.destroy()
            self.join_button.destroy()
            self.window.after(0,self.animation2)
            self.data = b""
            self.game_started=False
            def pro():
                self.data = b""
                self.client.setblocking(0)
                try:
                    chunk = self.client.recv(1024)
                    if chunk:
                        self.data += chunk
                except BlockingIOError:
                    pass 
                if self.data:
                    print("returning data: in joinGame",self.data)
                    msg=self.data.decode('utf-8')

                    self.dataDict=json.loads(msg)
                    print(self.dataDict)
                    print(self.dataDict['list'])
                    self.host_list=list(self.dataDict['list'].keys())
                    print(self.host_list," ",type(self.host_list))

                    if not self.host_list:
                        if hasattr(self, 'progressbar') and self.progressbar is not None:
                            self.progressbar.stop()

                        if hasattr(self, 'waiting_label') and self.waiting_label is not None:
                            self.waiting_label.destroy()

                        if hasattr(self, 'waiting_frame') and self.waiting_frame is not None:
                            self.waiting_frame.destroy()

                        messagebox.showwarning("No games found", "Try hosting the game")
                        self.window.after(0, self.main)
                        return None
                    else:
                        if hasattr(self, 'progressbar') and self.progressbar is not None:
                            self.progressbar.stop()

                        if hasattr(self, 'waiting_label') and self.waiting_label is not None:
                            self.waiting_label.destroy()

                        if hasattr(self, 'waiting_frame') and self.waiting_frame is not None:
                            self.waiting_frame.destroy()


                        self.current_index = 0  # Index to keep track of the current host in the list
                        self.label_frame = ttk.Frame(self.window, padding=(10, 10, 10, 10), style='LabelFrame.TFrame')
                        self.label_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                        self.label = ttk.Label(self.label_frame, text="", font=('Arial', 16), style='HostLabel.TLabel')
                        self.label.pack()
                        # Buttons to navigate through the list
                        self.left_button = tk.Button(self.window, text="prev", command=self.prevHost, bg='blue', fg='white', font=('Arial', 14))
                        self.left_button.place(relx=0.35, rely=0.5, anchor=tk.CENTER)
                        self.right_button = tk.Button(self.window, text="next", command=self.nextHost, bg='orange', fg='white', font=('Arial', 14))
                        self.right_button.place(relx=0.65, rely=0.5, anchor=tk.CENTER)
                        self.start_button = tk.Button(self.window, text="Start", command=self.startHost, bg='green', fg='white', font=('Arial', 14))
                        self.start_button.place(relx=0.5, rely=0.65, anchor=tk.CENTER) 
                        self.window.bind("<Return>", lambda event=None: self.hostname_enter()) 
                        self.window.bind("<Left>", lambda event=None: self.prevHost()) 
                        self.window.bind("<Right>", lambda event=None: self.nextHost()) 
                        self.updateLabel()  # Update the label initially
                if not self.game_started:
                    self.window.after(500, pro)
            self.window.after(0,pro)
        except Exception as e:
            print("some errror occured ",e)
            import traceback
            import sys
            traceback.print_exc()
            print("Something went wrong at line {}: {}".format(sys.exc_info()[-1].tb_lineno, str(e)))

    def updateLabel(self):
        host_name = self.host_list[self.current_index]
        num_players = self.dataDict['list'][host_name]  # Replace with the actual number of players
        self.label.config(text=f"Host: {host_name}\nNumber of Players: {num_players}")
    def prevHost(self):
        self.slideLabel('right')
        self.current_index = (self.current_index - 1) % len(self.host_list)
        self.updateLabel()
    def nextHost(self):
        self.slideLabel('left')
        self.current_index = (self.current_index + 1) % len(self.host_list)
        self.updateLabel()
    def slideLabel(self, direction):
        slide_from = -1 if direction == 'left' else 1
        slide_to = 0
        # Slide effect using ttk.Animation
        slide_animation = ttk.Style()
        slide_animation.configure('HostLabel.TLabel', padding=(slide_from, 0, slide_to, 0))
        self.label_frame.style = 'LabelFrame.TFrame'
        self.label_frame.configure(style='LabelFrame.TFrame')

    def startHost(self):
        try:
            selected_host = self.host_list[self.current_index]
            print(f"Starting host: {selected_host}, number of players {self.dataDict['list'][selected_host]}, if  of type {type(self.dataDict['list'][selected_host])}")

            #........
            self.game_started=True
            if(self.dataDict['list'][selected_host]==2):
                print("game room full")
                messagebox.showwarning("game full","game full try some other")
                if messagebox.askyesno("inspect?", "Do u want to inspect this game?"):
                    self.window.after(0,self.inspect(selected_host))
                else:
                    self.label_frame.destroy()
                    self.label.destroy()
                    self.left_button.destroy()
                    self.start_button.destroy()
                    self.right_button.destroy()
                    self.right_button.destroy()
                    self.window.after(0,self.main)    

            else:    
                try:
                    self.client.send(json.dumps({'type':'joinRoom','gameRoom':selected_host}).encode('utf-8'))
                    self.gameroom+=selected_host
                    self.label_frame.destroy()
                    self.label.destroy()
                    self.left_button.destroy()
                    self.start_button.destroy()
                    self.right_button.destroy()
                    self.right_button.destroy()
                    self.window.after(0,self.create_main_page)
                except Exception as e:
                    print(f"Connection error: {e}")
                    time.sleep(2)
                    messagebox.showwarning("NO game found", "no game found in this try other or room full")
                    sp.speech("NO GAME FOUND IN THIS HOST RETRY")
                    time.sleep(1) 
        except Exception as e:
            print("error in joining :",str(e));      
            import traceback
            import sys
            traceback.print_exc()
            print("Something went wrong at line {}: {}".format(sys.exc_info()[-1].tb_lineno, str(e)))           


    def goBack(self):
        exit(0)
        print("Back button clicked")

    def onEnter(self, event, button):
        button.config(bg="dark" + button.cget("bg"))

    def onLeave(self, event, button):
        button.config(bg=button.cget("bg")[4:])



    def clear_placeholder(self, event):
        if self.entry_alias.get() == 'Enter Alias Name':
            self.entry_alias.delete(0, tk.END)
    def restore_placeholder(self, event):
        if not self.entry_alias.get():
            self.entry_alias.insert(0, 'Enter Alias Name')


    def inspect(self,selected_host):
        self.window.configure(bg='#333333')
        self.client.send(json.dumps({'type':'inspectRoom','message':selected_host}).encode('utf-8'))
        self.alias_label = tk.Label(self.window, font=('Arial', 12))
        self.alias_label.grid(row=0, column=1, pady=(0, 10), sticky="nsew")
        self.opponent_label = tk.Label(self.window, font=('Arial', 12))
        self.opponent_label.grid(row=4, column=1, rowspan=2, sticky="nsew")
        exit_button = tk.Button(self.window, text="Exit", command=self.on_exit_inspect, bg='#FF0000', fg='white',font=('Arial', 12))
        exit_button.grid(row=6, column=0, pady=10, padx=5, sticky="nsew")
        for i in range(3):
            row_but = []
            for j in range(3):
                button = tk.Button(self.window, text="", font=("Arial", 50), anchor="center", height=2, width=6,
                                bg="lightblue") #initially set the state as disabled 
                button.grid(row=i + 1, column=j, sticky="nsew")
                row_but.append(button)
            self.buttons.append(row_but)

        #revieve boardState and pront them.. type:boardState,board:[....] ,palyerX: name....}
        
        # send {type: inspect status: start}     when game starts
        def recieving():
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
                    messages = self.data.decode('utf-8')
                    json_array_string = f'[{messages.replace("}{", "},{")}]'
                    messages=json.loads(json_array_string)

                    for data in messages:
                        if data['type']=='boardState':
                            
                            print("boardState: ",data['boardState'])
                            for i in range(3):
                                for j in range(3):
                                    if data['boardState'][i][j]=='X':
                                        self.buttons[i][j].config(text=data['boardState'][i][j], fg="red")
                                    elif data['boardState'][i][j]:
                                        self.buttons[i][j].config(text=data['boardState'][i][j], fg="blue")
                                    else:
                                        self.buttons[i][j].config(text="")
                            self.alias_label.config(text=f"payer1 : {data['playerX']}")
                            self.opponent_label_label.config(text=f"payer2 : {data['playerO']}")        
                                
                        if data['type']=='move':
                            if data['playerSymbol']=='X':
                                color='red'
                            else:
                                color='blue'
                            self.buttons[data['row']][data['col']].config(text=data['playerSymbol'], fg=color)
                        if data['type']=='gameEnd':
                                center_frame = tk.LabelFrameFrame(self.window, bg='#A9A9A9')
                                center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                                label=tk.Label(center_frame,text="player "+data['winAlias']+ "wins", width=30, font=('Arial', 16))
                                label.pack(pady=20)
                                time.sleep(2)
                                center_frame.destroy()
                                label.destroy()
                                #reset all positions
                                for i in range(3):
                                    for j in range(3):
                                        self.buttons[i][j].config(text="")

                        #when a player joins send both players username to inspect part...only
                        if data['type']=='nameLabel':
                            self.alias_label.config(text=f"payer1 : {data['player1']}")
                            self.opponent_label_label.config(text=f"payer2 : {data['player2']}")

                        if data['type']=="exit":  #when both players exit
                            #destry everything
                            self.alias_label.destroy()
                            self.opponent_label.destroy()
                            self.exit_button.destroy()
                            for i in range(3):
                                for j in range(3):
                                    self.buttons[i][j].destroy()
                            #disconnect from the server:     
                            self.window.after(0,self.main)

            except Exception as e:
                import traceback
                import sys
                traceback.print_exc()
                print("Something went wrong at line {}: {}".format(sys.exc_info()[-1].tb_lineno, str(e)))
            self.window.after(0,recieving)    
        recieving()          

    def on_exit_inspect(self):
        self.client.send(json.dumps({'type':'inspectExit'}))
        self.alias_label.destroy()
        self.opponent_label.destroy()
        self.exit_button.destroy()
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].destroy()
        #disconnect from the server:     
        self.window.after(0,self.main)
                                            
#----------------------------------------------------STARTING OF GAME------------------------------------------------------#
    def create_main_page(self):           
        sp.speech("Welcome to the game buddy")
        self.alias = ""
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

    def animation2(self):
        self.waiting_frame = tk.Frame(self.window, bg='#333333')
        self.waiting_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.waiting_label = tk.Label(self.waiting_frame, text="Searching for game", font=('Arial', 14), foreground='white', background='#333333')
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
            print("game room selecte is :",self.gameroom)
            self.client.send(json.dumps({'type': 'alias', 'message': self.alias,'gameRoom':self.gameroom,'id':self.id}).encode('utf-8'))
            print("message sent alias enter")
            responses=[]
            while True:
                # Set the socket to non-blocking mode
                self.client.setblocking(0)
                self.data = b""
                try:
                    chunk = self.client.recv(1024)
                    if chunk:
                        self.data += chunk
                except BlockingIOError:
                    pass 
                except ConnectionAbortedError as ex:
                    print("ConnectionAbortedError:", ex)
                    exit(0)
                if self.data:
                    print("in aliass enter ",self.data)
                    msg = self.data.decode('utf-8')
                    responses.append(json.loads(msg))
                    break
                time.sleep(0.2)
            response=responses[0]
            print("im here.. in alias enter")
            print(response)
            if response['type'] != 'nameError':
                print("creating threads...")
                self.client.send(json.dumps({'type':'joined'}).encode())
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
                                self.mySymbol=self.data['playerSymbol']
                                if self.data['playerSymbol']!="X":
                                    self.flag=True
                                print("opponent is ", self.data['user'])
                                self.opponent += self.data['user']
                                self.window.after(0, self.create_board)
                                self.window.after(0, self.handle_clicks)
                                return
                    except Exception as e:
                        import traceback
                        import sys
                        traceback.print_exc()
                        print("Something went wrong at line {}: {}".format(sys.exc_info()[-1].tb_lineno, str(e)))

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
            print("in after process :)")
            spectcount=0
            self.eye_label = tk.Label(self.window, text=f"👁️ {spectcount}", font=('Arial', 20))
            self.eye_label.grid(row=0, column=0, sticky="nsew")
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
            if self.mySymbol!='X':
                self.nameLabel.config(text="Your play",fg="red")
            else:    
                self.nameLabel.config(text="opponents play",fg="blue") # Pass the callback function to process   
        except Exception as e:
            print(f"An error occurred during GUI update: {str(e)}")
    def handle_click(self,row,col):
        if self.client.fileno() == -1:
            print("Socket closed")
            return
        if self.buttons[row][col].cget('state')=='normal' and self.flag:
            d={'type':'move','message':{'row':row,'col':col},'gameRoom':self.gameroom}
            json_data=json.dumps(d)
            print(json_data)
            while True:
                self.client.setblocking(0)
                try:
                    self.client.send(json_data.encode('utf-8'))
                    break
                except BlockingIOError:
                    pass
                except Exception as e:
                    print(f"Error occurred during send operation: {e}")
                    pass
            self.l.append([row,col])
            
            while True:
                self.client.setblocking(0)
                try:
                    data=json.loads(self.client.recv(1024).decode('utf-8'))
                    print(f"IN create-board-handle-clicks {data} ")
                    break
                except BlockingIOError:
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
                    self.buttons[data['row']][data['col']].config(text=data['playerSymbol'], fg=color)  #disable the button which is clicked
                    self.flag=False
                    self.nameLabel.config(text="opponents play",fg="blue")
                elif data['type']=='invalidMove':
                    messagebox.showerror("invalid move"," Already clicked")    
                elif data['type'] == 'gameEnd':
                    print("game End msg: ",data)
                    if data['winAlias'] == self.alias:
                        #make all winning 
                        self.buttons[data['winSeq']['row1']][data['winSeq']['col1']].config(bg="green")
                        self.buttons[data['winSeq']['row2']][data['winSeq']['col2']].config(bg="green")
                        self.buttons[data['winSeq']['row3']][data['winSeq']['col3']].config(bg="green")
                        
                        messagebox.showinfo("Congratulations", "You won :)")
                        sp.praise("Congratulations you won")
                        r=messagebox.askyesno("Restart","restart the game ?  ")
                        if r:
                            self.window.after(0,self.reset_board)
                        else:
                            self.on_exit() 
                    elif data['draw']=='1':
                        messagebox.showinfo("draw","its a draw.. :)")
                        sp.speech("its a Draw")
                        r=messagebox.askyesno("Restart","restart the game ?  ")
                        if r:
                            self.window.after(0,self.reset_board)
                        else:
                            self.on_exit()  
                    else:
                        messagebox.showinfo("Oops!! You Lost")
                        sp.con("Oops you lost it, better luck next time")
                        r=messagebox.askyesno("Restart","restart the game ?  ")
                        if r:
                            self.window.after(0,self.reset_board)
                        else:
                            self.on_exit() 
                else:
                    self.l.pop()       
            except Exception as e:
                print('Error!',str(e))
                exit(0)
                self.client.close()
        else:
            messagebox.showwarning('warning','sorry pal you cant click this other payer needs to play!') 
            sp.speech("sorry pal you cant click this other payer needs to play")
#-------------------------------------------------------------------------------------------------------------------------------#
    #voice message
    #chat room
    #Emoji colletions:
#----------------------------------------------------------------------------------------------#
    #exit and reset querries
    def emoji_select(self):
# Define the directory path
        emoji_directory = 'client/emojis/'

        # Create emoji data with relative paths
        emoji_data = [
            (emoji_directory + 'u0001f44a.png', '\U0001F44A'),
            (emoji_directory + 'u0001f44c.png', '\U0001F44C'),
            (emoji_directory + 'u0001f44d.png', '\U0001F44D'),
            (emoji_directory + 'u0001f495.png', '\U0001F495'),
            (emoji_directory + 'u0001f496.png', '\U0001F496'),
            (emoji_directory + 'u0001f4a6.png', '\U0001F4A6'),
            (emoji_directory + 'u0001f4a9.png', '\U0001F4A9'),
            (emoji_directory + 'u0001f4af.png', '\U0001F4AF'),
            (emoji_directory + 'u0001f595.png', '\U0001F595'),
            (emoji_directory + 'u0001f600.png', '\U0001F600'),
            (emoji_directory + 'u0001f602.png', '\U0001F602'),
            (emoji_directory + 'u0001f603.png', '\U0001F603'),
            (emoji_directory + 'u0001f605.png', '\U0001F605'),
            (emoji_directory + 'u0001f606.png', '\U0001F606'),
            (emoji_directory + 'u0001f608.png', '\U0001F608'),
            (emoji_directory + 'u0001f60d.png', '\U0001F60D'),
            (emoji_directory + 'u0001f60e.png', '\U0001F60E'),
            (emoji_directory + 'u0001f60f.png', '\U0001F60F'),
            (emoji_directory + 'u0001f610.png', '\U0001F610'),
            (emoji_directory + 'u0001f618.png', '\U0001F618'),
            (emoji_directory + 'u0001f61b.png', '\U0001F61B'),
            (emoji_directory + 'u0001f61d.png', '\U0001F61D'),
            (emoji_directory + 'u0001f621.png', '\U0001F621'),
            (emoji_directory + 'u0001f624.png', '\U0001F621'),
            (emoji_directory + 'u0001f631.png', '\U0001F631'),
            (emoji_directory + 'u0001f632.png', '\U0001F632'),
            (emoji_directory + 'u0001f634.png', '\U0001F634'),
            (emoji_directory + 'u0001f637.png', '\U0001F637'),
            (emoji_directory + 'u0001f642.png', '\U0001F642'),
            (emoji_directory + 'u0001f64f.png', '\U0001F64F'),
            (emoji_directory + 'u0001f920.png', '\U0001F920'),
            (emoji_directory + 'u0001f923.png', '\U0001F923'),
            (emoji_directory + 'u0001f928.png', '\U0001F928')
        ]


        def button_click(emoji):
            self.message_entry.delete(0,tk.END)
            self.message_entry.insert(tk.END, emoji)

        self.root = tk.Tk()
        self.root.title("Emoji Selector")

        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0)

        for i, (image_path, emoji) in enumerate(emoji_data):
            row = i // 7
            col = i % 7
            button = ttk.Button(frame)
            button.grid(row=row, column=col, padx=5, pady=5)
            emoji_image = tk.PhotoImage(file=image_path)
            button.config(image=emoji_image, command=lambda emoji=emoji: button_click(emoji))
            button.image = emoji_image  # to prevent garbage collection of the image

        self.root.mainloop()

    def create_chatroom(self, master):
        chatroom_frame = tk.Frame(master, bg='#115C54')
        chatroom_frame.grid(row=0, column=3, padx=20, rowspan=7, sticky="nsew")

        self.chat_display = tk.Text(chatroom_frame, state='disabled', width=30, height=30, bg='white', font=('Arial', 14))
        self.chat_display.grid(row=0, column=0, padx=15, pady=10, columnspan=5, sticky="nsew")

        self.message_entry = tk.Entry(chatroom_frame, width=40, font=('Arial', 14))
        self.message_entry.insert(0, "Type a message")
        self.message_entry.bind("<FocusIn>", self.on_entry_click)
        self.message_entry.bind("<FocusOut>", self.on_focus_out)
        self.message_entry.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        self.message_entry.bind("<Return>", self.send_message_enter)

        self.send_button = tk.Button(chatroom_frame, text="🎤", command=self.voiceMessage, bg='#3B945E', fg='white', font=('Arial', 14))
        self.send_button.grid(row=4, column=1, padx=10, pady=5, sticky="e")
        self.emoji_button = tk.Button(chatroom_frame, text="😀", command=self.emoji_select)
        self.emoji_button.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        self.chat_display.tag_configure('message_box', background='#DCF8C6', foreground='#000000', relief='raised')
        self.chat_display.tag_configure('message_text', foreground='#000000')

    def sendMsg(self):
        self.send_button.config(text="🎤", command=self.voiceMessage)
        print("sending encoded voice message")
        self.window.after(0, self.send_message)

    def voiceMessage(self):
        print("voice message")
        if self.message_entry.get() == "Type a message":
            self.message_entry.delete(0, "end")
        res = messagebox.askyesno("voice", "Start voice message?")
        if res:
            msg = b""
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Voice Typing started. Speak now...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio)
                    print("You said:", text)
                    self.message_entry.insert(tk.END, text)
                    self.send_button.config(text="❌", command=self.sendMsg)
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if self.root:
            self.root.destroy()
        if message:
            self.client.send(json.dumps({'type': 'chat', 'message': message,'gameRoom':self.gameroom}).encode('utf-8'))
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
            if self.root:
                self.root.destroy()

            self.message_entry.delete(0, "end")
            self.send_button.config(command=self.send_message, text="➤")
            self.message_entry.config(fg="black")

    def on_focus_out(self, event):
        if self.root:
            self.root.destroy()
        if self.message_entry.get() == "":
            self.message_entry.insert(0, "Type a message")
            self.send_button.config(command=self.voiceMessage, text="🎤")
            self.message_entry.config(fg="grey")

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message)
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)              
    def on_exit(self,event=None):
        
        result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if result:
            self.client.send(json.dumps({'type': 'exit', 'alias': self.alias,'gameRoom':self.gameroom,'id':self.id}).encode('utf-8'))
            self.window.destroy()
            TicTacToeGame()
        else:
            if event==True:
                self.flag=False
                for i in range(3):
                    for j in range(3):
                        if [i, j] not in self.l:
                            self.buttons[i][j].config(state=tk.DISABLED)
    def handle_clicks(self):
        def process_server_errors():
            try:
                # Set the socket to non-blocking mode
                self.client.setblocking(0)
                data=b""
                try:
                    chunk = self.client.recv(1024)
                    if chunk:
                        data += chunk
                except BlockingIOError:
                    pass  # No data received, continue with non-blocking operations
                #print("in handle clicks",data)
                if data:
                    print("in handle clicks",data)
                    messages = data.decode('utf-8')
                    json_array_string = f'[{messages.replace("}{", "},{")}]'
                    messages=json.loads(json_array_string)
                    for data in messages:
                        print("in handle clicks: ",data)
                        if data['type'] == 'exit':
                            messagebox.showinfo('Player Left', 'Opponent left the game')
                        elif data['type'] == 'noPlayer':
                            messagebox.showwarning('Wait Pal', 'Hey buddy, wait for player 2 to join')
                        elif data['type'] == 'restart':
                            res = messagebox.askyesno('Restart', 'Opponent requested a restart. Do you agree?')
                            self.client.send(json.dumps({'type': 'restart', 'val': '1' if res else '0','gameRoom':self.gameroom,'id':self.id}).encode('utf-8'))
                        elif data['type'] == 'reset' and data['val']=='1':
                            messagebox.showinfo("","RESTARTING THE GAME")
                            self.window.after(0,self.reset_board)    
                        elif data['type'] == "join":
                            messagebox.showinfo('Joined', f'Opponent {data["user"]} joined the game')
                            self.progressbar.stop()
                            self.waiting_label.destroy()
                            self.waiting_frame.destroy()  
                            self.opponent_label.config(text=data['user'])
                        if data['type'] == 'chat':
                            print(data['message'])  # Make it print in chatbot gui
                            self.display_message(f" {data['message']}\n")    
                            self.opponent_label.config(text=data['user'])
                        elif data['type']=="invalidMoveError":
                            messagebox.showerror("error","invalid moove") 
                        elif data['type']=="playerLeft":
                            messagebox.showinfo("playerleft","opponent left the game")   
                            self.window.after(0,self.reset_board)
                            self.window.after(0,self.animation)
                        elif data['type'] == 'gameEnd':
                            print("game End msg: ",data)
                            if 'winAlias' in data and data['winAlias'] == self.alias:
                                self.buttons[data['winSeq']['row1']][data['winSeq']['col1']].config(bg="green")
                                self.buttons[data['winSeq']['row2']][data['winSeq']['col2']].config(bg="green")
                                self.buttons[data['winSeq']['row3']][data['winSeq']['col3']].config(bg="green")
                                messagebox.showinfo("Congratulations", "You won :)")
                                sp.praise("Congratulations you won")
                                r=messagebox.askyesno("Restart","restart the game ?  ")
                                if r:
                                    self.window.after(0,self.reset_board)
                                else:
                                    self.on_exit() 
                            elif data['draw']=='1':
                                messagebox.showinfo("draw","its a draw.. :)")
                                sp.speech("its a Draw")   
                                r=messagebox.askyesno("Restart","restart the game ?  ")
                                if r:
                                    self.window.after(0,self.reset_board)
                                else:
                                    self.on_exit()  
                            else:
                                messagebox.showinfo("Oops!!   You Lost")
                                sp.con(":(","Oops you lost it, better luck next time")
                                r=messagebox.askyesno("Restart","restart the game ?  ")
                                if r:
                                    self.window.after(0,self.reset_board)
                                else:
                                    self.on_exit(True)   
                        elif data['type']=='move':
                                    if not self.flag: 
                                            try:
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
                                                        self.nameLabel.config(fg="red",text="Your Play")
                                            except Exception as e:
                                                import traceback
                                                traceback.print_exc()
                                                print("Something went wrong:", str(e))

                        elif data['type']=='spectatorLeft':
                            self.eye_label.config(text=f"👁️ {data['count']}")     

            except Exception as e:
                import traceback
                traceback.print_exc()
                print("Something went wrong:", str(e))     
            self.window.after(100, process_server_errors)
        # Initial call to start the loop
        process_server_errors()
    def reset_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state=tk.NORMAL,bg="lightblue")
        self.l = []
        if self.mySymbol=='X':
            self.flag=False
            self.nameLabel.config(fg="blue",text="Opponents Play")
        else:
            self.flag=True
            self.nameLabel.config(fg="red",text="Your Play")
    def reset(self):
        self.client.send(json.dumps({'type':'restart','message':1,'gameRoom':self.gameroom,'id':self.id}).encode('utf-8'))
        self.window.after(0,self.reset_board)               
if __name__ == "__main__":
    while True:
        game = TicTacToeGame()
