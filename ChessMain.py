import pygame as p
import ChessEngine
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    colour = ["w", "b"]
    pieces = ["P", "R", "N", "K", "Q", "B"]

    for side in colour:
        for piece in pieces:
            name = side+piece
            temp_image = p.image.load("images/"+name+".png")
            IMAGES[name] = p.transform.scale(temp_image, (SQ_SIZE, SQ_SIZE))
            # print(temp_image, IMAGES)


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    board_colours = [p.Color("white"), p.Color("gray")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            temp_rect = p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            if ((r+c) % 2) == 0:
                p.draw.rect(screen, board_colours[0], temp_rect)
            else:
                p.draw.rect(screen, board_colours[1], temp_rect)


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            temp_rect = p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE)

            piece_name = board[row][col]

            if piece_name != "--":
                # draw image with given location
                screen.blit(IMAGES[piece_name], temp_rect)


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected == ():
        return
    r, c = sqSelected
    if(gs.inCheck() == True and gs.whiteToMove):
        sq = p.Surface((SQ_SIZE, SQ_SIZE))
        sq.set_alpha(80)
        sq.fill(p.Color("red"))
        # draw this object
        screen.blit(
            sq, (gs.whiteKingLocation[1] * SQ_SIZE, gs.whiteKingLocation[0] * SQ_SIZE))

    if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
        sq = p.Surface((SQ_SIZE, SQ_SIZE))
        sq.set_alpha(80)  # set transparency
        sq.fill(p.Color("blue"))
        screen.blit(sq, (c*SQ_SIZE, r*SQ_SIZE))  # draw this object
        sq.fill(p.Color("yellow"))
        for move in validMoves:
            if move.startRow == r and move.startCol == c:
                screen.blit(sq, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def drawText(screen, text):
    font = p.font.SysFont("comicsansms", 32, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)


def turnText(isWhiteToMove):
    return "White's Turn" if isWhiteToMove else "Black's Turn"


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMove()
    moveMade = False
    ChessEngine.print_text_board(gs.board)
    loadImages()
    running = True
    sqSelected = ()  # box clicked by the user (row,col)
    playerClicks = []  # all clicks by user [(row,col),(row,col)]
    gameOver = False
    p.display.set_caption(turnText(gs.whiteToMove))

    while running:
        for event in p.event.get():
            if not gs.whiteToMove:
                move = aimove(gs, 3)
                gs.makeMove(move)
                moveMade = True
                p.display.set_caption(turnText(gs.whiteToMove))
                print(len(gs.moveLog))
            if event.type == p.QUIT:
                running = False
            # mouse handel
            elif event.type == p.MOUSEBUTTONDOWN and gs.whiteToMove:  # mouse press
                if gameOver == True:
                    break
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:  # two box selected move the piece
                    move = ChessEngine.Move(
                        playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    print(playerClicks)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            print("moved here:", move.endRow, move.endCol)
                            if validMoves[i].isPawnPromotion:
                                print("Promote to:")
                                new_piece = input().upper()
                                validMoves[i].promotionChoice = new_piece if new_piece in (
                                    "Q", "R", "N", "B") else "Q"
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            p.display.set_caption(turnText(gs.whiteToMove))
                            sqSelected = ()
                            playerClicks = []
                            break
                    if not moveMade:
                        playerClicks = [sqSelected]

            # key handel
            if event.type == p.KEYDOWN and gs.whiteToMove:
                if event.key == p.K_z:  # z to undo move
                    gs.undoMove()
                    gs.undoMove()
                    moveMade = True
                    p.display.set_caption(turnText(gs.whiteToMove))

                if event.key == p.K_c:  # c to clear variables
                    sqSelected = ()
                    playerClicks = []
                if event.key == p.K_f:  # f to print valid moves
                    for i in validMoves:
                        print(i.startRow, i.startCol, i.endRow, i.endCol)
                if event.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMove()
                    playerClicks = []
                    sqSelected = ()
                    moveMade = False
                    p.display.set_caption(turnText(gs.whiteToMove))

        if moveMade:
            validMoves = gs.getValidMove()
            moveMade = False
            p.display.set_caption(turnText(gs.whiteToMove))

        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black WON by checkmate")
            else:
                drawText(screen, "White WON by checkmate")
        clock.tick(MAX_FPS)
        p.display.flip()


def evaluate(gs):
    pawntable = [[0,  0,  0,  0,  0,  0,  0,  0],
                 [50, 50, 50, 50, 50, 50, 50, 50],
                 [10, 10, 20, 30, 30, 20, 10, 10],
                 [5,  5, 10, 25, 25, 10,  5,   5],
                 [0,  0,  0, 20, 20,  0,  0,   0],
                 [5, -5, -10,  0,  0, -10, -5,  5],
                 [5, 10, 10, -20, -20, 10, 10,   5],
                 [0,  0,  0,  0,  0,  0,  0,   0]]
    knighttable = [[-50, -40, -30, -30, -30, -30, -40, -50],
                   [-40, -20,  0,  0,  0,  0, -20, -40],
                   [-30,  0, 10, 15, 15, 10,  0, -30],
                   [-30,  5, 15, 20, 20, 15,  5, -30],
                   [-30,  0, 15, 20, 20, 15,  0, -30],
                   [-30,  5, 10, 15, 15, 10,  5, -30],
                   [-40, -20,  0,  5,  5,  0, -20, -40],
                   [-50, -40, -30, -30, -30, -30, -40, -50]]
    bishoptable = [[-20, -10, -10, -10, -10, -10, -10, -20, ],
                   [-10,  0,  0,  0,  0,  0,  0, -10, ],
                   [-10,  0,  5, 10, 10,  5,  0, -10, ],
                   [-10,  5,  5, 10, 10,  5,  5, -10, ],
                   [-10,  0, 10, 10, 10, 10,  0, -10, ],
                   [-10, 10, 10, 10, 10, 10, 10, -10, ],
                   [-10,  5,  0,  0,  0,  0,  5, -10, ],
                   [-20, -10, -10, -10, -10, -10, -10, -20, ]]
    rooktable = [[0, 0, 0, 0, 0, 0, 0, 0],
                 [5, 10, 10, 10, 10, 10, 10,  5],
                 [-5,  0,  0,  0,  0,  0,  0, -5],
                 [-5,  0,  0,  0,  0,  0,  0, -5],
                 [-5,  0,  0,  0,  0,  0,  0, -5],
                 [-5,  0,  0,  0,  0,  0,  0, -5],
                 [-5,  0,  0,  0,  0,  0,  0, -5],
                 [0, 0, 0, 5, 5, 0, 0, 0]]
    queentable = [[-20, -10, -10, -5, -5, -10, -10, -20],
                  [-10,  0,  0,  0,  0,  0,  0, -10],
                  [-10,  0,  5,  5,  5,  5,  0, -10],
                  [-5,  0,  5,  5,  5,  5,  0, -5],
                  [0,  0,  5,  5,  5,  5,  0, -5],
                  [-10,  5,  5,  5,  5,  5,  0, -10],
                  [-10,  0,  5,  0,  0,  0,  0, -10],
                  [-20, -10, -10, -5, -5, -10, -10, -20]]
    kingtable = [[-30, -40, -40, -50, -50, -40, -40, -30],
                 [-30, -40, -40, -50, -50, -40, -40, -30],
                 [-30, -40, -40, -50, -50, -40, -40, -30],
                 [-30, -40, -40, -50, -50, -40, -40, -30],
                 [-20, -30, -30, -40, -40, -30, -30, -20],
                 [-10, -20, -20, -20, -20, -20, -20, -10],
                 [20, 20,  0,  0,  0,  0, 20, 20],
                 [20, 30, 10,  0,  0, 10, 30, 20]]

    if gs.checkMate:
        if gs.whiteToMOve:
            return -10000
        else:
            return 10000
    if gs.staleMate:
        return 0
    wp = 0
    wr = 0
    wn = 0
    wb = 0
    wq = 0
    bp = 0
    br = 0
    bn = 0
    bb = 0
    bq = 0

    score = 0
    for i in range(8):
        for j in range(8):
            if gs.board[i][j][0] == 'b':
                if gs.board[i][j][1] == 'P':
                    score += pawntable[i][j]
                    bp += 1
                if gs.board[i][j][1] == 'R':
                    score += rooktable[i][j]
                    br += 1
                if gs.board[i][j][1] == 'N':
                    score += knighttable[i][j]
                    bn += 1
                if gs.board[i][j][1] == 'B':
                    score += bishoptable[i][j]
                    bb += 1
                if gs.board[i][j][1] == 'Q':
                    score += queentable[i][j]
                    bq += 1
                if gs.board[i][j][1] == 'K':
                    score += kingtable[i][j]
            if gs.board[i][j][0] == 'w':
                if gs.board[i][j][1] == 'P':
                    score -= pawntable[7-i][7-j]
                    wp += 1
                if gs.board[i][j][1] == 'R':
                    score -= rooktable[7-i][7-j]
                    wr += 1
                if gs.board[i][j][1] == 'N':
                    score -= knighttable[7-i][7-j]
                    wn += 1
                if gs.board[i][j][1] == 'B':
                    score -= bishoptable[7-i][7-j]
                    wb += 1
                if gs.board[i][j][1] == 'Q':
                    score -= queentable[7-i][7-j]
                    wq += 1
                if gs.board[i][j][1] == 'K':
                    score -= kingtable[7-i][7-j]
    diff = 100 * (wp-bp) + 320 * (wn-bn) + 330 * (wb-bb) + 500 * (
        wr-br) + 900 * (wq-bq)
    score += diff
    if gs.whiteToMove:
        return score
    else:
        return -score


def minimaxalphabeta(gs, alpha, beta, depth):
    if(depth == 0):
        return evaluate(gs)
    maxscore = -10000
    moves = gs.getValidMove()
    for move in moves:
        if move.isPawnPromotion:
            move.promotionChoice = 'Q'
        gs.makeMove(move)
        score = minimaxalphabeta(gs, -beta, -alpha, depth-1)
        gs.undoMove()
        if(score >= beta):
            return score
        if(score > maxscore):
            maxscore = score
        if(score > alpha):
            alpha = score
    return maxscore


def aimove(gs, depth):
    machmove = None
    maxval = -99999
    alpha = -100000
    beta = 100000
    moves = gs.getValidMove()
    for move in moves:
        if move.isPawnPromotion:
            move.promotionChoice = 'Q'
        gs.makeMove(move)
        val = -minimaxalphabeta(gs, -beta, -alpha, depth-1)
        gs.undoMove()
        if(val > maxval):
            maxval = val
            machmove = move
        if(val > alpha):
            alpha = val
    return machmove


if __name__ == "__main__":
    main()
