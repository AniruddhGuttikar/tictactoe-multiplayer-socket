import net from 'net'
import dotenv from 'dotenv'

dotenv.config()

const PORT = process.env.PORT; // Choose a port for the server
const HOST = process.env.HOST; // Listen on all network interfaces

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
    
    const aliasMessage = {
        type: 'alias',
        message: 'enter the username'
    }
    socket.write(JSON.stringify(aliasMessage));

    // Handle data from clients
    socket.on('data', (data) => {
        const {type, message} = JSON.parse(data);
        if (type === "alias") {
            const playerName = message

            if (clients.length < 2) {
                clients.push(socket);
                socket.playerSymbol = clients.length === 0 ? "X" : "O"
            } else {
                console.error("Room is already full");
                socket.destroy({
                    type: 'roomFullError',
                    message: 'room is already full'
                })
                return
            }

            if (clients.length > 1 && playerName === clients[0].playerName) {
                const errorInfo = {
                    type: 'nameError',
                    message: 'please choose a different username'
                }
                socket.write(JSON.stringify(errorInfo))
            } else {
                socket.playerName = playerName
                const joinInfo = {
                    type: 'join',
                    user: socket.playerName,
                }
                console.log(`${socket.playerName} has joined the game`)
                clients.forEach(client => {
                    if (!client.destroyed) {
                        client.write(JSON.stringify(joinInfo))
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
                    client.write(JSON.stringify(chatData));
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
                const invalidMoveError = {
                    type: "invalidMoveError",
                    message: "invalid move",
                    player: socket.playerName,
                }
                socket.write(JSON.stringify(invalidMoveError))
            }
        }
        if (type === "restart") {
            const isRestart = message;
            socket.isRestart = isRestart === '1' ? true : false;
            if (socket.isRestart === false) {
                const index = clients.indexOf(socket);
                socket.destroy()
                if (index !== -1) {
                    clients.splice(index, 1);
                }
            }
            const allPlayersReady = clients.every(client => client.isRestart)
            if (allPlayersReady && clients.length === 2) {
                console.log("Restarting the game")
                const restartInfo = {
                    type: 'restart',
                    message: '1',
                }
                clients.forEach(client => {
                    if (!client.destroyed) {
                        socket.write(JSON.stringify(restartInfo));
                    }
                })
            } else {
                console.log("can't restart the game yet")
                const restartInfo = {
                    type: 'restart',
                    message: '0',
                }
                clients.forEach(client => {
                    if (!client.destroyed) {
                        socket.write(JSON.parse(restartInfo))
                    }
                })
            }
        }
    });

    // Handle client disconnection
    socket.on('close', () => {
        console.log(`${socket.playerName} has disconnected`);
        // Remove the client from the list
        const index = clients.indexOf(socket);
        if (index !== -1) {
            clients.splice(index, 1);
        }
        const closeInfo = {
            type: "playerLeft",
            player: socket.playerName
        }
        if (clients.length) {
            clients[0].write(JSON.stringify(closeInfo))
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
{        
        for (let i = 0; i < 3; i++) {
            if (gameState[i][0] !== '0' && gameState[i][0] === gameState[i][1] && gameState[i][1] === gameState[i][2]) {
                return gameState[i][0]; 
            }
        } 
        
        for (let i = 0; i < 3; i++) {
            if (gameState[0][i] !== '0' && gameState[0][i] === gameState[1][i] && gameState[1][i] === gameState[2][i]) {
                return gameState[0][i]; 
            }
        }
        
        if (gameState[0][0] !== '0' && gameState[0][0] === gameState[1][1] && gameState[1][1] === gameState[2][2]) {
            return gameState[0][0]; 
        }

        if (gameState[0][2] !== '0' && gameState[0][2] === gameState[1][1] && gameState[1][1] === gameState[2][0]) {
            return gameState[0][2]; 
        }
        
        
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
            return 'draw'; 
        }
        
        return 'ongoing';} 
    
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
            client.write(JSON.stringify(gameStateMsg));
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
            client.write(JSON.stringify(endMsg))
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
    //clients.length = 0;
}

// Start the server
server.listen(PORT, HOST, () => {
    console.log(`Server listening on ${HOST}:${PORT}`);
});
