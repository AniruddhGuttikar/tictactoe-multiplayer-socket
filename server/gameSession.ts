import net from "net"

type PlayerSymbol = 'X' | 'O'

export interface Player {
    id: string
    socket: net.Socket
    symbol: PlayerSymbol
    name?: string
}

export interface Spectator {
    id: string
    socket: net.Socket
}

type gameEndInfo = {
    winSymbol: string;
    winSeq: {
      row1: number;
      row2: number;
      row3: number;
      col1: number;
      col2: number;
      col3: number;
    };
}

type gameEnd = string | gameEndInfo

export default class GameSession {
    gameName: string
    host: Player
    players: Player[]
    spectators: Spectator[]
    board: string[][]
    turn: PlayerSymbol

    constructor(gameName: string, host: Player) {
        this.gameName = gameName
        this.host = host
        this.players = [host]
        this.spectators = []
        this.turn = 'X'  
        this.board = [
            ['0', '0', '0'], 
            ['0', '0', '0'],
            ['0', '0', '0'],
        ];
    }
    
    addPlayer(Player: Player): boolean {
        if (this.players.length < 2) {
            this.players.push(Player)
            return true
        } else {
            return false
        }
    }

    addSpectator(spectator: Spectator): boolean {
        if (!this.spectators.includes(spectator)) {
            this.spectators.push(spectator)
            return true
        } else {
            return false
        }
    }

    returnPlayers(): Player[] {
        return [...this.players]
    }

    removePlayer(player: Player): void {
        this.players = this.players.filter(p => p !== player);
    }

    isValidMove(row: number, col: number): boolean {
        return this.board[row][col] === '0'
    }

    makeMove(row: number, col: number): boolean {
        if (this.isValidMove(row, col)) {
            this.board[row][col] = this.turn
            this.turn = this.turn === "X" ? "O" : "X" 
            return true
        }
        return false
    }

    broadcastMove(playerSymbol: PlayerSymbol , row: number, col: number): void {
        const moveInfo = {
            type: "move",
            playerSymbol,
            row,
            col,
        }
        for (const p of this.players) {
            p.socket.write(JSON.stringify(moveInfo))
        }
        console.log("data sent: ", moveInfo)
        for (const s of this.spectators) {
            s.socket.write(JSON.stringify(moveInfo))
        }
    }

    checkGameResult(): gameEnd { 
        for (let i = 0; i < 3; i++) {
            //check rows
            if (this.board[i][0] !== '0' && this.board[i][0] === this.board[i][1] && this.board[i][1] === this.board[i][2]) {
                return {
                    winSymbol: this.board[i][0],
                    winSeq: {
                        row1: i, col1: 0,
                        row2: i, col2: 1,
                        row3: i, col3: 2,
                    }
                }
            }
        } 
        //check columns
        for (let i = 0; i < 3; i++) {
            if (this.board[0][i] !== '0' && this.board[0][i] === this.board[1][i] && this.board[1][i] === this.board[2][i]) {
                return {
                    winSymbol: this.board[0][i],
                    winSeq: {
                        row1: 0, col1: i,
                        row2: 1, col2: i,
                        row3: 2, col3: i,
                    }
                }
            }
        }

        //check each diagonals
        if (this.board[0][0] !== '0' && this.board[0][0] === this.board[1][1] && this.board[1][1] === this.board[2][2]) {
            return ({
                winSymbol: this.board[0][0],
                winSeq: {
                    row1: 0, col1: 0,
                    row2: 1, col2: 1,
                    row3: 2, col3: 2,
                }
            })
        }

        if (this.board[0][2] !== '0' && this.board[0][2] === this.board[1][1] && this.board[1][1] === this.board[2][0]) {
            return ({
                winSymbol: this.board[0][2],
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
                if (this.board[i][j] === '0') {
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

    handleGameEnd = (result: gameEnd) => {
        //result is 'draw' | struct
        if (result === 'draw') {
            const endMsg = {
                type: "gameEnd",
                draw: '1', 
            }
            this.players.forEach(p => {
                if (!p.socket.destroyed) {
                    p.socket.write(JSON.stringify(endMsg))
                }
            })
            this.spectators.forEach(sp => {
                if (!sp.socket.destroyed) {
                    sp.socket.write(JSON.stringify(endMsg))
                }
            })
        } else {
            const winAlias = this.players.find(p => p.symbol === (result as gameEndInfo).winSymbol)?.name
            const endMsg = {
                ...(result as gameEndInfo),
                type: "gameEnd",
                draw: '0',
                winAlias,
            }
            this.players.forEach(p => {
                if (!p.socket.destroyed) {
                    p.socket.write(JSON.stringify(endMsg))
                }
            })
            this.spectators.forEach(sp => {
                if (!sp.socket.destroyed) {
                    sp.socket.write(JSON.stringify(endMsg))
                }
            })
        }
        this.resetGame()
    }

    resetGame = () => {
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                this.board[i][j] = '0';
            }
        }
        this.turn = 'X'
    }
}
