const net = require('net');

const PORT = 3000; // Choose a port for the server
const HOST = '0.0.0.0'; // Listen on all network interfaces

// Create a TCP server
const server = net.createServer();

const clients = [];

const gameState = [
    ['0', '0', '0'], 
    ['0', '0', '0'],
    ['0', '0', '0'],
];

// Handle new connections
server.on('connection', (socket) => {
    //console.log('A new client connected:', socket.remoteAddress);
    socket.write('alias');

    // Handle data from clients
    socket.on('data', (data) => {
        const {type, message} = JSON.parse(data);
        if (type === "alias") {
            if (clients.length < 2) {
                clients.push(socket);
                socket.playerSymbol = clients.length === 0 ? "X" : "O"
            }
            if (clients.length > 1) {
                console.error("Room is already full");
                socket.destroy({
                    type: 'roomFullError',
                    message: 'room is already full'
                })
                return
            }
            socket.playerName = message;

            if (clients.length > 1 && socket.playerName === clients[0].playerName) {
                const errorInfo = {
                    type: 'nameError',
                    message: 'please choose a different username'
                }
                socket.write(errorInfo)
            } else {
                const joinInfo = {
                    type: 'join',
                    user: socket.playerName,
                }
                console.log(`${socket.playerName} has joined the game`)
                clients.forEach(client => {
                    if (client !== socket && !client.destroyed) {
                        client.write(joinInfo)
                    }
                })
            }

        }

        if (type === "chat") {
            const chatData = {
                type: "chat",
                user: socket.playerName,
                message,
            }

            clients.forEach((client) => {
                if (client !== socket && !client.destroyed) {
                    client.write(chatData);
                }
            });
            console.log(`${socket.playerName}: ${message}`)
        }

        if (type === "move") {
            const {row, col} = message;
            
            if (isValidMove(row, col)) {
                gameState(row, col) = socket.playerSymbol
            }
            const gameResult = checkGameResult(gameState)

            broadcastGameState(row, col, socket.playerSymbol)
            
            if (gameResult !== "ongoing") {
                handleGameEnd(gameResult)
            } else {
                console.error("invalid move")
                socket.write("invalid move - from the server")
            }
        }

 
    });

    // Handle client disconnection
    socket.on('close', () => {
        console.log('A client disconnected:', socket.remoteAddress);
        // Remove the client from the list
        const index = clients.indexOf(socket);
        if (index !== -1) {
            clients.splice(index, 1);
        }
    });

    // Handle errors
    socket.on('error', (err) => {
        console.error('Socket error:', err.message);
    });
});

const isValidMove = (row, col) => {
    return gameState[row][col] === '0'
}

const checkGameResult = () => {
{        // Check rows
        for (let i = 0; i < 3; i++) {
            if (gameState[i][0] !== '0' && gameState[i][0] === gameState[i][1] && gameState[i][1] === gameState[i][2]) {
                return gameState[i][0]; // Return the winning player symbol
            }
        }
        
        // Check columns
        for (let i = 0; i < 3; i++) {
            if (gameState[0][i] !== '0' && gameState[0][i] === gameState[1][i] && gameState[1][i] === gameState[2][i]) {
                return gameState[0][i]; // Return the winning player symbol
            }
        }
        
        // Check diagonals
        if (gameState[0][0] !== '0' && gameState[0][0] === gameState[1][1] && gameState[1][1] === gameState[2][2]) {
            return gameState[0][0]; // Return the winning player symbol
        }
        if (gameState[0][2] !== '0' && gameState[0][2] === gameState[1][1] && gameState[1][1] === gameState[2][0]) {
            return gameState[0][2]; // Return the winning player symbol
        }
        
        // Check for draw
        let isDraw = true;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (gameState[i][j] === '0') {
                    isDraw = false;
                    break;
                }
            }
            if (!isDraw) {
                break;
            }
        }
        if (isDraw) {
            return 'draw'; // Return 'draw' if the game ended in a draw
        }
        
        return 'ongoing';} // Return 'ongoing' if the game is still in progress
    
}
const broadcastGameState = (row, col, playerSymbol) => {
    const gameStateMsg = {
        type: "move",
        playerSymbol,
        row,
        col, 
    };
    clients.forEach((client) => {
        if (!client.destroyed) {
            client.write(gameStateMsg);
        }
    });
}

const handleGameEnd = (result) => {
    const endMsg = {
        type: "gameEnd",
        result,
    }
    clients.forEach(client => {
        if (!client.destroyed) {
            client.write(endMsg)
        }
    })
    resetGame()
}

const resetGame = () => {
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            gameState[i][j] = '0';
        }
    }
    clients.length = 0;
}

// Start the server
server.listen(PORT, HOST, () => {
    console.log(`Server listening on ${HOST}:${PORT}`);
});
