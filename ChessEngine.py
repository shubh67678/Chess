import pygame


class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.loopFunctions = {"P": self.getPawnMoves, "R": self.getRockMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves, "N": self.getNightMoves}
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castlingRightsLog = []
        self.castlingRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                   self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        self.enpassantPossible = ()

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # king position keep track
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        # Pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +\
                move.promotionChoice
        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        # moving twice
        if move.pieceMoved[1] == "P" and abs(move.startRow-move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow+move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
        # castle move
        if move.isCastleMove:
            # king side
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][move.endCol+1]  # move rook
                self.board[move.endRow][move.endCol+1] = "--"  # erase rook
            # queen side
            else:
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        # Castling rights
        self.updateCastleRights(move)
        self.castlingRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                   self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    def undoMove(self):
        if len(self.moveLog) > 0:
            last_move = self.moveLog.pop()
            self.board[last_move.startRow][last_move.startCol] = last_move.pieceMoved
            self.board[last_move.endRow][last_move.endCol] = last_move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # track kings
            if last_move.pieceMoved == "wK":
                self.whiteKingLocation = (
                    last_move.startRow, last_move.startCol)
            elif last_move.pieceMoved == "bK":
                self.blackKingLocation = (
                    last_move.startRow, last_move.startCol)
            # undo enpassant
            if last_move.isEnpassantMove:
                self.board[last_move.endRow][last_move.endCol] = "--"
                self.board[last_move.startRow][last_move.endCol] = last_move.pieceCaptured
                self.enpassantPossible = (last_move.endRow, last_move.endCol)
            # undo add to enpassant if moved twice
            if last_move.pieceMoved[1] == "P" and abs(last_move.startRow-last_move.endRow) == 2:
                self.enpassantPossible = ()
            # undo castle rights
            self.castlingRightsLog.pop()
            newRights = self.castlingRightsLog[-1]
            self.currentCastlingRights = CastleRights(
                newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # undo castle
            if last_move.isCastleMove:
                # king side
                if last_move.endCol - last_move.startCol == 2:
                    # move rook
                    self.board[last_move.endRow][last_move.endCol +
                                                 1] = self.board[last_move.endRow][last_move.endCol - 1]
                    self.board[last_move.endRow][last_move.endCol -
                                                 1] = "--"  # erase rook
                # queen side
                else:
                    self.board[last_move.endRow][last_move.endCol -
                                                 2] = self.board[last_move.endRow][last_move.endCol + 1]
                    self.board[last_move.endRow][last_move.endCol + 1] = "--"

    def getValidMove(self):
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        tempEnpassantPossible = self.enpassantPossible
        # generate all moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # for each move make a move
        for i in range(len(moves)-1, -1, -1):  # backwards to delete the list item
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove  # to not let go of the turn
            # generate all opponent moves
            if self.inCheck():
                # see if king is save
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves

    def inCheck(self):
        # verify if the king is in CHECK
        # print("white:", self.whiteKingLocation[0], self.whiteKingLocation[1])
        # print("black:", self.blackKingLocation[0], self.blackKingLocation[1])
        if self.whiteToMove == True:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove
        opponent_moves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove

        for move in opponent_moves:
            if move.endRow == row and move.endCol == col:
                # print("The row,col ", row, col)
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                turn = self.board[row][col][0]
                if (turn == "w" and self.whiteToMove == True) or (turn == "b" and self.whiteToMove == False):
                    piece = self.board[row][col][1]
                    self.loopFunctions[piece](row, col, moves)
        return moves

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove == True:
            if self.board[row-1][col] == "--":  # move up once
                moves.append(Move((row, col), (row-1, col), self.board))
                # move up twice if first move
                if row == 6 and self.board[row-2][col] == "--":
                    moves.append(Move((row, col), (row-2, col), self.board))

            side_col = col-1
            next_row = row-1
            if self.inside_board(side_col, next_row) and self.board[next_row][side_col][0] == "b":
                moves.append(
                    Move((row, col), (next_row, side_col), self.board))
            elif self.inside_board(side_col, next_row) and (next_row, side_col) == self.enpassantPossible:
                moves.append(
                    Move((row, col), (next_row, side_col), self.board, isEnpassantMove=True))

            side_col = col+1
            next_row = row-1
            if self.inside_board(side_col, next_row) and self.board[next_row][side_col][0] == "b":
                moves.append(
                    Move((row, col), (next_row, side_col), self.board))
            elif self.inside_board(side_col, next_row) and (next_row, side_col) == self.enpassantPossible:
                moves.append(
                    Move((row, col), (next_row, side_col), self.board, isEnpassantMove=True))

        else:
            # move up once
            if self.inside_board(row+1, col) and self.board[row+1][col] == "--":
                moves.append(Move((row, col), (row+1, col), self.board))
                # move up twice if first move
                if row == 1 and self.board[row+2][col] == "--":
                    moves.append(Move((row, col), (row+2, col), self.board))

            side_col = col-1
            next_row = row+1
            if self.inside_board(side_col, next_row) and self.board[next_row][side_col][0] == "w":
                moves.append(
                    Move((row, col), (next_row, side_col), self.board))
            elif self.inside_board(side_col, next_row) and (next_row, side_col) == self.enpassantPossible:
                moves.append(
                    Move((row, col), (next_row, side_col), self.board, isEnpassantMove=True))

            side_col = col+1
            next_row = row+1
            if self.inside_board(side_col, next_row) and self.board[next_row][side_col][0] == "w":
                moves.append(
                    Move((row, col), (next_row, side_col), self.board))
            elif self.inside_board(side_col, next_row) and (next_row, side_col) == self.enpassantPossible:
                moves.append(
                    Move((row, col), (next_row, side_col), self.board, isEnpassantMove=True))

    def getRockMoves(self, row, col, moves):
        directions = ((0, 1), (1, 0), (-1, 0), (0, -1))
        enemyColor = "b" if self.whiteToMove == True else "w"

        for d in directions:
            for i in range(1, 8):
                next_row = row + d[0]*i
                next_col = col + d[1]*i
                if self.inside_board(next_row, next_col) == False:
                    break
                if self.board[next_row][next_col] == "--":
                    moves.append(
                        Move((row, col), (next_row, next_col), self.board))
                    continue
                if self.board[next_row][next_col][0] == enemyColor:
                    moves.append(
                        Move((row, col), (next_row, next_col), self.board))
                    break
                else:
                    break

    def getBishopMoves(self, row, col, moves):
        directions = ((1, 1), (-1, -1), (-1, 1), (1, -1))
        enemyColor = "b" if self.whiteToMove == True else "w"

        for d in directions:
            for i in range(1, 8):
                next_row = row + d[0]*i
                next_col = col + d[1]*i
                if self.inside_board(next_row, next_col) == False:
                    break
                if self.board[next_row][next_col] == "--":
                    moves.append(
                        Move((row, col), (next_row, next_col), self.board))
                    continue
                if self.board[next_row][next_col][0] == enemyColor:
                    moves.append(
                        Move((row, col), (next_row, next_col), self.board))
                    break
                else:
                    break

    def getQueenMoves(self, row, col, moves):
        directions = ((0, 1), (1, 0), (-1, 0), (0, -1),
                      (1, 1), (-1, -1), (-1, 1), (1, -1))
        enemyColor = "b" if self.whiteToMove == True else "w"

        for d in directions:
            for i in range(1, 8):
                next_row = row + d[0]*i
                next_col = col + d[1]*i
                if self.inside_board(next_row, next_col) == False:
                    break
                if self.board[next_row][next_col] == "--":
                    moves.append(
                        Move((row, col), (next_row, next_col), self.board))
                    continue
                if self.board[next_row][next_col][0] == enemyColor:
                    moves.append(
                        Move((row, col), (next_row, next_col), self.board))
                    break
                else:
                    break

    def getKingMoves(self, row, col, moves):
        directions = ((0, 1), (1, 0), (-1, 0), (0, -1),
                      (1, 1), (-1, -1), (-1, 1), (1, -1))
        enemyColor = "b" if self.whiteToMove == True else "w"

        for d in directions:
            next_row = row + d[0]
            next_col = col + d[1]
            if self.inside_board(next_row, next_col) == False:
                continue
            elif self.board[next_row][next_col] == "--":
                moves.append(
                    Move((row, col), (next_row, next_col), self.board))
                continue
            elif self.board[next_row][next_col][0] == enemyColor:
                moves.append(
                    Move((row, col), (next_row, next_col), self.board))

    def getNightMoves(self, row, col, moves):
        directions = ((-2, -1), (-2, 1), (2, -1), (2, 1),
                      (-1, -2), (-1, 2), (1, -2), (1, 2))
        enemyColor = "b" if self.whiteToMove == True else "w"

        for d in directions:
            next_row = row + d[0]
            next_col = col + d[1]
            if self.inside_board(next_row, next_col) == False:
                continue
            elif self.board[next_row][next_col] == "--":
                moves.append(
                    Move((row, col), (next_row, next_col), self.board))
                continue
            elif self.board[next_row][next_col][0] == enemyColor:
                moves.append(
                    Move((row, col), (next_row, next_col), self.board))

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        if move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        if move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        if move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

    def inside_board(self, row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return True
        return False

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2),
                                  self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--":
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move((row, col), (row, col-2),
                                  self.board, isCastleMove=True))


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    # opposite of ranksToRows
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2,
                   'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    # opposite of filesToCols
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSQ, endSQ, board, promotionChoice="Q", isCastleMove=False, isEnpassantMove=False):
        self.startRow = startSQ[0]
        self.startCol = startSQ[1]
        self.endRow = endSQ[0]
        self.endCol = endSQ[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol
        self.promotionChoice = promotionChoice if promotionChoice in (
            "Q", "R", "N", "B") else "Q"
        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        self.isCastleMove = isCastleMove

    def getChessNotation(self):
        # gets standard notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col]+self.rowsToRanks[row]

    def __eq__(self, other):
        if isinstance(other, Move):  # other is move type
            return self.moveID == other.moveID
        return False


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # white king side
        self.bks = bks  # Black king side
        self.wqs = wqs  # white queen side
        self.bqs = bqs  # black queen side


def print_text_board(arr):
    for i in arr:
        for j in i:
            print(j, end=" ")
        print()
def evalmove(move):
    score = 0
    if move.pieceMoved[0] == 'b':
        if move.pieceMoved[1] == 'P':
            score -= (pawntable[move.endRow][move.endCol] - pawntable[move.startRow][move.startCol])
        if move.pieceMoved[1] == 'R':
            score -= (rooktable[move.endRow][move.endCol] - rooktable[move.startRow][move.startCol])
        if move.pieceMoved[1] == 'N':
            score -= (knighttable[move.endRow][move.endCol] - knighttable[move.startRow][move.startCol])
        if move.pieceMoved[1] == 'B':
            score -= (bishoptable[move.endRow][move.endCol] - bishoptable[move.startRow][move.startCol])
        if move.pieceMoved[1] == 'Q':
            score -= (queentable[move.endRow][move.endCol] - queentable[move.startRow][move.startCol])
        if move.pieceMoved[1] == 'K':
            score -= (kingtable[move.endRow][move.endCol] - kingtable[move.startRow][move.startCol])
    if move.pieceMoved[0] == 'w':
        if move.pieceMoved[1] == 'P':
            score += (
                        pawntable[7 - move.endRow][7 - move.endCol] - pawntable[7 - move.startRow][7 - move.startCol])
        if move.pieceMoved[1] == 'R':
            score += (
                        rooktable[7 - move.endRow][7 - move.endCol] - rooktable[7 - move.startRow][7 - move.startCol])
        if move.pieceMoved[1] == 'N':
            score += (knighttable[7 - move.endRow][7 - move.endCol] - knighttable[7 - move.startRow][
                7 - move.startCol])
        if move.pieceMoved[1] == 'B':
            score += (bishoptable[7 - move.endRow][7 - move.endCol] - bishoptable[7 - move.startRow][
                7 - move.startCol])
        if move.pieceMoved[1] == 'Q':
            score += (
                        queentable[7 - move.endRow][7 - move.endCol] - queentable[7 - move.startRow][7 - move.startCol])
        if move.pieceMoved[1] == 'K':
            score += (
                        kingtable[7 - move.endRow][7 - move.endCol] - kingtable[7 - move.startRow][7 - move.startCol])
    if move.pieceCaptured!='--':
        if move.pieceCaptured[0]=='w':
            score-=piecevalues[move.pieceCaptured[1]]
            if move.pieceCaptured[1] == 'P':
                score -= (
                        pawntable[7 - move.endRow][7 - move.endCol] )
            if move.pieceCaptured[1] == 'R':
                score -= (
                        rooktable[7 - move.endRow][7 - move.endCol])
            if move.pieceCaptured[1] == 'N':
                score -= (knighttable[7 - move.endRow][7 - move.endCol] )
            if move.pieceCaptured[1] == 'B':
                score -= (bishoptable[7 - move.endRow][7 - move.endCol] )
            if move.pieceCaptured[1] == 'Q':
                score -= (
                        queentable[7 - move.endRow][7 - move.endCol] )
            if move.pieceCaptured[1] == 'K':
                score -= (
                        kingtable[7 - move.endRow][7 - move.endCol])
        else:
            score += piecevalues[move.pieceCaptured[1]]
            if move.pieceCaptured[1] == 'P':
                score += (
                        pawntable[move.endRow][move.endCol] )
            if move.pieceCaptured[1] == 'R':
                score += (
                        rooktable[move.endRow][move.endCol])
            if move.pieceCaptured[1] == 'N':
                score += (knighttable[move.endRow][move.endCol] )
            if move.pieceCaptured[1] == 'B':
                score += (bishoptable[move.endRow][move.endCol] )
            if move.pieceCaptured[1] == 'Q':
                score += (
                        queentable[move.endRow][move.endCol] )
            if move.pieceCaptured[1] == 'K':
                score += (
                        kingtable[move.endRow][move.endCol])

    #print("The eval score is "+str(score))
    return score

