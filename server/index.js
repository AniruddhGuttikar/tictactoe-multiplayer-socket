import net from 'net'
import dotenv from 'dotenv'
import gameSession from './gameSession'

dotenv.config()

const PORT = process.env.PORT; // Choose a port for the server
const HOST = process.env.HOST; // Listen on all network interfaces

// Create a TCP server
const server = net.createServer();

//contains sessionId and game
const ongoingGames = new Map()

// Handle new connections
server.on('connection', async (socket) => {
    
    const ongoingGamesArray = [...ongoingGames.values().gameName]

    const aliasMessage = {
        type: 'alias',
        message: 'enter the username',
    }
    socket.write(JSON.stringify(aliasMessage));

    // Handle data from clients
    socket.on('data', async (data) => {
        const {type, message} = JSON.parse(data);

        if (type === "alias") {
            const playerName = message

            if (clients.length < 2) {
                if (clients.length === 0) {
                    socket.playerSymbol = 'X'
                } else {
                    socket.playerSymbol = clients[0].playerSymbol === 'X' ? 'O' : 'X'
                }
                clients.push(socket);
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
                    playerSymbol: socket.playerSymbol,
                }
                console.log(`${socket.playerName} has joined the game`)
                clients.forEach(client => {
                    if (!client.destroyed) {
                        client.write(JSON.stringify(joinInfo))
                        console.log(`sending .... ${client.playerName} first time`)
                    }
                })
                if (clients.length === 2) {
                    clients[1].write(JSON.stringify({
                        type: 'join',
                        user: clients[0].playerName,
                        playerSymbol: clients[0].playerSymbol,
                    }))
                    console.log(`sending ${clients[1].playerName} second time`)
                }
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
            console.log('data received: ', JSON.parse(data))
            console.log(`${socket.playerSymbol} has made a move`)
            console.log('row, col', row, col)
            if (isValidMove(row, col)) {
                gameState[row][col] = socket.playerSymbol
                broadcastGameState(row, col, socket.playerSymbol)
            } else {
                console.log("invalid move")
                const invalidMoveError = {
                    type: "invalidMoveError",
                    message: "invalid move",
                    player: socket.playerName,
                }
                socket.write(JSON.stringify(invalidMoveError))
            }
            //gets ongoing | draw | the struct
            const gameResult = checkGameResult()

            if (gameResult !== 'ongoing') {
                handleGameEnd(gameResult)
            }
        }

        if (type === "restart") {
            const isRestart = message;
            socket.isRestart = isRestart === 1 ? true : false;
            if (socket.isRestart === false) {
                const index = clients.indexOf(socket);
                socket.destroy()
                if (index !== -1) {
                    clients.splice(index, 1);
                }
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
        resetGame()
    });

    // Handle errors
    socket.on('error', (err) => {
        console.error('Socket error:', err.message);
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
        resetGame()
    });
});


// Start the server
server.listen(PORT, HOST, () => {
    console.log(`Server listening on ${HOST}:${PORT}`);
});
