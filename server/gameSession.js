class gameSession {
    constructor(gameName, host) {
        this.gameName = gameName
        this.host = host
        this.players = [host]
        this.spectators = []
        this.board = [
            ['0', '0', '0'], 
            ['0', '0', '0'],
            ['0', '0', '0'],
        ];
    }
    
    addPlayer(player) {
        if (this.players.size < 2) {
            this.players.push(player)
            return true
        } else {
            return false
        }
    }

    addSpectator(spectator) {
        if (!this.spectators.includes(spectator)) {
            this.spectators.push(spectator)
            return true
        } else {
            return false
        }
    }

    returnPlayers() {
        return [...this.players]
    }

    removePlayer(id) {
        const index = this.players.findIndex(player => player.remoteAddress)
        if (index != -1) {
            this.players.splice(index, 1)
            return {
                status: 'true',
                message: 'player removed successfully'
            }
        } else {
            return false
        }
    }

    isValidMove = (row, col) => {
        return this.board[row][col] === '0'
    }

    checkGameResult = () => { 
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

    handleGameEnd = (result) => {
        //result is 'draw' | struct
        if (result === 'draw') {
            const endMsg = {
                type: "gameEnd",
                draw: '1', 
            }
            this.players.forEach(player => {
                if (!player.destroyed) {
                    player.write(JSON.stringify(endMsg))
                }
            })
        } else {
    
            const winAlias = this.players.find(player => player.playerSymbol === result.winSymbol).playerName
            const endMsg = {
                ... result,
                type: "gameEnd",
                draw: '0',
                winAlias,
            }
            this.players.forEach(player => {
                if (!player.destroyed) {
                    player.write(JSON.stringify(endMsg))
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
    }
}

export default gameSession