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
server.on('connection', async (socket) => {
    
    const aliasMessage = {
        type: 'alias',
        message: 'enter the username'
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
            // const allPlayersReady = clients.every(client => client.isRestart)
            // if (allPlayersReady && clients.length === 2) {
            //     console.log("Restarting the game")
            //     const restartInfo = {
            //         type: 'restart',
            //         message: 1,
            //     }
            //     clients.forEach(client => {
            //         if (!client.destroyed) {
            //             socket.write(JSON.stringify(restartInfo));
            //         }
            //     })
            // } else {
            //     console.log("can't restart the game yet")
            //     const restartInfo = {
            //         type: 'restart',
            //         message: 0,
            //     }
            //     clients.forEach(client => {
            //         if (!client.destroyed) {
            //             socket.write(JSON.parse(restartInfo))
            //         }
            //     })
            // }
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

const isValidMove = (row, col) => {
    return gameState[row][col] === '0'
}

//return winSeq and the winSymbol
const checkGameResult = () => { 
        for (let i = 0; i < 3; i++) {
            //check rows
            if (gameState[i][0] !== '0' && gameState[i][0] === gameState[i][1] && gameState[i][1] === gameState[i][2]) {
                return ({
                    winSymbol: gameState[i][0],
                    winSeq: {
                        row1: i, col1: 0,
                        row2: i, col2: 1,
                        row3: i, col3: 2,
                    }
                })
            }
        } 
        //check columns
        for (let i = 0; i < 3; i++) {
            if (gameState[0][i] !== '0' && gameState[0][i] === gameState[1][i] && gameState[1][i] === gameState[2][i]) {
                return ({
                    winSymbol: gameState[0][i],
                    winSeq: {
                        row1: 0, col1: i,
                        row2: 1, col2: i,
                        row3: 2, col3: i,
                    }
                }) 
            }
        }
        //check each diagonals
        if (gameState[0][0] !== '0' && gameState[0][0] === gameState[1][1] && gameState[1][1] === gameState[2][2]) {
            return ({
                winSymbol: gameState[0][0],
                winSeq: {
                    row1: 0, col1: 0,
                    row2: 1, col2: 1,
                    row3: 2, col3: 2,
                }
            })
        }

        if (gameState[0][2] !== '0' && gameState[0][2] === gameState[1][1] && gameState[1][1] === gameState[2][0]) {
            return ({
                winSymbol: gameState[0][2],
                winSeq: {
                    row1: 0, col1: 2,
                    row2: 1, col2: 1,
                    row3: 2, col3: 0,
                }
            })
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
        
    return 'ongoing';
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
    //result is 'draw' | struct
    if (result === 'draw') {
        const endMsg = {
            type: "gameEnd",
            draw: '1', 
        }
        clients.forEach(client => {
            if (!client.destroyed) {
                client.write(JSON.stringify(endMsg))
            }
        })
    } else {

        const winAlias = clients.find(client => client.playerSymbol === result.winSymbol).playerName
        const endMsg = {
            ... result,
            type: "gameEnd",
            draw: '0',
            winAlias,
        }
        clients.forEach(client => {
            if (!client.destroyed) {
                client.write(JSON.stringify(endMsg))
            }
        })
    }
    
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
