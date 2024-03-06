import net from 'net'
import dotenv from 'dotenv'
import GameSession, { Player } from './gameSession.js'
import { Socket } from 'dgram'


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
            const { gameRoom } = data

            const game = returnGame(gameRoom)
            // if the game with the same name already exists
            if (game) {
                const nameError = {
                    type: "nameError",
                    message: "game name already exists"
                }
                socket.write(JSON.stringify(nameError))
                return
            }
            const player: Player = {
                socket,
                symbol: 'X'
            }
            const newGame = new GameSession(gameRoom, player)
            newGame.host = player
            ongoingGames.push(newGame)
            const createInfo = {
                type: "gameCreated",
                message: "game has started"
            }
            socket.write(JSON.stringify(createInfo))
            return
        }

        // need to send the list of all the games available to the joinee
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
            const { gameRoom } = data
            const game = returnGame(gameRoom)
            if (!game) {
                socket.destroy()
                console.log("invalid game room")
                return
            }

            const player: Player = {
                socket,
                symbol: 'O'
            }
            game.addPlayer(player)
            return
        }

        if (type === "inspectRoom") {
            const {gameRoom} = data

            const game = returnGame(gameRoom)
            if (!game) {
                console.error("game not found")
                return
            }

            const isAdded = game.addSpectator(socket)
            if (isAdded) {
                const spectatorJoinInfo = {
                    type: "spectatorJoin",
                    count: game.spectators.length
                }
                console.log(`${game.gameName}: a wild spectator has been found lurking around`)

                // send all the players updated spectator count
                game.players.forEach(player => {
                    player.socket.write(JSON.stringify(spectatorJoinInfo))
                })

                //send spectator the currant board state
                const boardStateMsg = {
                    type: "boardState",
                    boardState: game.board
                }
                socket.write(JSON.stringify(boardStateMsg))
            } else {
                console.log(`${game.gameName}: couldn't add the spectator`)
                return
            }
            return
        }

        if (type === "alias") {
            const {gameRoom, message: playerName} = data

            // get the gameRoom of the player and update their name
            const game = returnGame(gameRoom)
            const player = returnPlayer(game, socket)

            if (!(game && player)) {
                console.error("couldn't find the Game or the player")
                return
            }

            player.name = playerName

            const joinInfo = {
                type: "join",
                user: player.name,
                playerSymbol: player.symbol
            }

            // if host just send them back their own joinInfo
            if (game.host.name === player.name) {
                player.socket.write(JSON.stringify(joinInfo))
                return
            }

            // if opponent then send opponent both the host and the opponent the joinInfo
            // sending opponent their own info - first time
            player.socket.write(JSON.stringify(joinInfo))
            // sending host the - second time
            game.host.socket.write(JSON.stringify(joinInfo))
            // sending opponent the host info -second time
            const hostInfo = {
                type: "join",
                user: game.host.name,
                playerSymbol: game.host.symbol
            }
            player.socket.write(JSON.stringify(hostInfo))
            return
        }

        if (type === "chat") {
            const {message, gameRoom} = data

            const game = returnGame(gameRoom)
            const player = returnPlayer(game, socket)

            if (!(game && player)) {
                console.error("couldn't find the Game or the player")
                return
            }

            const chatInfo = {
                type: "chat",
                user: player?.name,
                message,
            }

            game.players.forEach(p => {
                p.socket.write(JSON.stringify(chatInfo))
            })
            console.log(`in ${game.gameName}\n${player.name}: ${message}`)
            return
        }

        if (type === "move") {
            const {row, col, gameRoom} = data.message

            const game = returnGame(gameRoom)
            const player = returnPlayer(game, socket)

            if (!(game && player)) {
                console.error("couldn't find the Game or the player")
                return
            }

            console.log(`${game.gameName}\nmove made by ${player.name}: row: ${row} col: ${col}`)

            const isSuccess = game.makeMove(row, col)

            // send the moveInfo to all the players and spectators 
            if (!isSuccess) {
                console.log(`${game.gameName}: invalid move`)
                const invalidMoveError = {
                    type: "invalidMoveError",
                    message: "invalid move",
                    player: player.name,
                }
                socket.write(JSON.stringify(invalidMoveError))
            } else {
                game.broadcastMove(player.symbol, row, col)
            }

            // check if the game has ended 
            const gameResult = game.checkGameResult()
            if (gameResult !== 'ongoing') {
                game.handleGameEnd(gameResult)
            }
            return
        }

        if (type === "restart") {
            const {message: isRestart, gameRoom} = data

            const game = returnGame(gameRoom)
            const player = returnPlayer(game, socket)

            if (!(game && player)) {
                console.error("couldn't find the Game or the player")
                return
            }

            if (!isRestart) {
                socket.destroy()
                console.log(`${game.gameName}\n${player.name} has been kicked out of the game`)
            }
        }
    });

    // Handle client or spectator disconnection
    socket.on('close', () => {
        let player: Player | undefined
        let game: GameSession | undefined

        for (const g of ongoingGames) {
            player = returnPlayer(g, socket) 
            if (player) {
                game = g
                break
            }
        }

        // if player not found then it's the spectator who left the game
        if (!(game && player)) {
            // get the game where the spectator is present
            for (const g of ongoingGames) {
                for (const sp of g.spectators) {
                    if (sp.remoteAddress === socket.remoteAddress) {
                        game = g
                    }
                }
            }

            // update the spectator list
            if (game) {
                console.log(`${game.gameName}: a spectator left the game`)
                game.spectators = game.spectators.filter(sp => sp.remoteAddress !== socket.remoteAddress)
                const spectatorLeftInfo = {
                    type: "spectatorLeft",
                    count: game.spectators.length,
                }
                game.players.forEach((player) => {
                    player.socket.write(JSON.stringify(spectatorLeftInfo))
                })
            } else {
                console.error(`i have no idea who just left`)
            }
            return
        }

        console.log(`${game.gameName}: ${player.name} has disconnected`);

        // Remove the player from the game
        game.players = game.players.filter(p => p !== player)
        
        // if the player was the host and first to leave
        if (game.host === player && game.players.length === 1) {
            game.host = game.players[0]
            game.host.symbol = 'X'
        }

        // if the other player is still present 
        if (game.players.length) {
            const closeInfo = {
                type: "playerLeft",
                player: player.name
            }
            game.players[0].socket.write(JSON.stringify(closeInfo))
            game.spectators.forEach(sp => {
                sp.write(JSON.stringify(closeInfo))
            })
            game.resetGame()
        } else {
            // both the players left the game
            console.log(`from ${game.gameName}: all left the game`)
            // remove the game from the ongoingGames
            let gindex = ongoingGames.findIndex(g => g === game)
            if (gindex !== -1) {
                ongoingGames.splice(gindex, 1)

                const gameEndSpec = {
                    type: "gameEndSpec",
                    message: "current game has ended"
                }
                game.spectators.forEach(sp => {
                    sp.write(JSON.stringify(gameEndSpec))
                })
            }
        }
    })

    // Handle errors
    socket.on('error', (err) => {
        console.error("oopsies!! something went wrong: ", err.name, err.message)
        socket.destroy()
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

const returnPlayer = (gameRoom: GameSession | undefined, ip: net.Socket): Player | undefined => {
    if (gameRoom) {
        return gameRoom.players.find(p => p.socket.remoteAddress === ip.remoteAddress)
    } else {
        return undefined
    }
}

// Start the server
server.listen(PORT, HOST, (): void => {
    console.log(`Server listening on ${HOST}:${PORT}`);
});
