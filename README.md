# Tic-Tac-Toe Multiplayer Game with Sockets

This is a multiplayer Tic-Tac-Toe game implemented using TypeScript for the backend with Node.js and Tkinter for the client-side in Python. The game allows multiple users to play against each other, chat during gameplay, and spectate ongoing games. It utilizes socket communication for real-time interaction between players.

## Features

- **Multiplayer Gameplay**: Users can connect to the server and play Tic-Tac-Toe against each other in real-time.
- **Chat Functionality**: Players can chat with each other during gameplay to communicate or just have fun.
- **Multiple Games on the Same Server**: The server can handle multiple games simultaneously, allowing several pairs of players to play at once.
- **Spectate Option**: Users can choose to spectate ongoing games, observing the gameplay without participating.
- **Additional Frontend Features**: The frontend includes extra features such as themes, voice recognition, image capture, and video playback.

## Installation

### Backend (Node.js with TypeScript)

1. Clone the repository:

    ```bash
    git clone https://github.com/AniruddhGuttikar/tictactoe-multiplayer-socket
    ```

2. Navigate to the backend directory:

    ```bash
    cd backend
    ```

3. Install dependencies:

    ```bash
    npm install
    ```

4. Build the TypeScript code:

    ```bash
    npm run build 
    ```

### Client Side (Python with Tkinter)

1. Install Python (if not already installed).

2. Install required libraries:

    ```bash
    pip install ttkthemes pygame SpeechRecognition opencv-python Pillow moviepy
    ```

3. Navigate to the client directory:

    ```bash
    cd client
    ```

4. Run the client application:

    ```bash
    python client.py
    ```

## Usage

1. Start the server as mentioned in the backend installation steps.

2. Run the client application as mentioned in the client installation steps.

3. Connect to the server using the client application.

4. Start a new game or choose to spectate ongoing games.

5. Play Tic-Tac-Toe against another player or spectate ongoing games.

6. Utilize the chat functionality to communicate with other players.

7. Explore additional frontend features such as themes, voice recognition, image capture, and video playback.

## Contributing

Contributions are welcome! If you have any ideas for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the code for your own purposes.