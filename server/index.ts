import net from 'net'
import dotenv from 'dotenv'
import GameSession, { Player } from './gameSession.js'
import { spec } from 'node:test/reporters'

dotenv.config()

const PORT = parseInt(process.env.PORT || '3000') // Choose a port for the server
const HOST = process.env.HOST // Listen on all network interfaces

// Create a TCP server
const server = net.createServer();

// list contains all the ongoing games
const ongoingGames: GameSession[] = []

// Handle new connections
server.on('connection', async (socket) => {
    // Handle data from clients
    socket.on('data', async (data: any) => {
        const { type } = data

        if (type === "createGame") {
            let alreadyExists = false
            const gameName = data.message

            ongoingGames.forEach(game => {
                if (game.gameName === gameName) {
                    alreadyExists = true
                }
            })
            if (alreadyExists) {
                const nameError = {
                    type: "nameError",
                    message: "gamename already exists"
                }
                socket.write(JSON.stringify(nameError))
                return
            }
            const player: Player = {
                socket,
                symbol: 'X'
            }
            const newGame = new GameSession(gameName, player)
            ongoingGames.push(newGame)
            const createInfo = {
                type: "gameCreated",
                message: "game has started"
            }
            socket.write(JSON.stringify(createInfo))
            return
        }

// need to send the list of all the games availabe to the joinee
        if (type === "joinGame") {
            const gamesList: {[key: string]: number} = {}
            for (const game of ongoingGames) {
                gamesList[game.gameName] = game.players.length
            }
            const gamesInfo = {
                type: "gamesList",
                list: gamesList
            }
            socket.write(JSON.stringify(gamesInfo))
            return
        }
// joinRoom or inspectRoom
        if (type === "joinRoom") {
            const roomName = data.message
            const gameRoom = returnGame(roomName)
            const player: Player = {
                socket,
                symbol: 'O'
            }
            gameRoom?.addPlayer(player)
            return
        }
        
        if (type === "inspectRoom") {
            const roomName = data.message
            const gameRoom = returnGame(roomName)
            const spectator = socket
            gameRoom?.addSpectator(spectator)
            
            const boardStateMsg = {
                type: "boardState",
                boardState: gameRoom?.board
            }
            spectator.write(JSON.stringify(boardStateMsg))
            return
        }

        if (type === "alias") {
            const playerName = data.message
            const roomName = data.gameRoom

            // get the gameRoom of the player and update their name
            const gameRoom = returnGame(roomName)
            const player = gameRoom?.players.find(player => player.socket.remoteAddress === socket.remoteAddress)
            if (!player) {
                console.error("player doesn't exist")
                return
            }
            player.name = playerName

            const joinInfo = {
                type: "join",
                user: player.name,
                playerSymbol: player.symbol
            }
            // if host just send them back their own joinInfo
            if (gameRoom?.host.name === player.name) {
                player.socket.write(JSON.stringify(joinInfo))
                return
            }
            // if opponet then send opponent both the host and the apponent the joinInfo
            // sending opponet their own info - first time
            player.socket.write(JSON.stringify(joinInfo))
            // sending host the - second time
            gameRoom?.host.socket.write(JSON.stringify(joinInfo))
            // sending opponent the host info -second time
            

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
    });
});

const returnGame = (gameName: string): GameSession | undefined => {
    for (const game of ongoingGames) {
        if (game.gameName === gameName) {
            return game
        }
    }
    console.error("game room not found")
    return undefined
}


// Start the server
server.listen(PORT, HOST, (): void => {
    console.log(`Server listening on ${HOST}:${PORT}`);
});
