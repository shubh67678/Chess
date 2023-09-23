import pygame as p
import ChessEngine
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    color = ["w", "b"] # typo 
    pieces = ["P", "R", "N", "K", "Q", "B"]

    for side in color:
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
    board_colors = [(184, 139, 74), (227, 193, 111)]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            temp_rect = p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            if ((r+c) % 2) == 0:
                p.draw.rect(screen, board_colors[0], temp_rect)
            else:
                p.draw.rect(screen, board_colors[1], temp_rect)


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


def turnText(isWhiteToMove) -> str :
    return "White's Turn" if isWhiteToMove else "Black's Turn"


def drawOptionBox(screen, human, computer):
    # draw option box
    window = p.Surface((6*SQ_SIZE, 4*SQ_SIZE))
    window.fill(p.Color("yellow"))
    screen.blit(window, (1*SQ_SIZE, 2*SQ_SIZE))

    # draw option text
    font = p.font.SysFont("comicsansms", 32, True, False)
    textObject = font.render("Play Against ", True, p.Color("Black"))
    textLocation = textObject.get_rect()
    textLocation.center = (WIDTH//2, 3*SQ_SIZE)
    screen.blit(textObject, textLocation)

    # draw human and computer icon
    location = p.Rect(2*SQ_SIZE, 4*SQ_SIZE, SQ_SIZE, SQ_SIZE)
    screen.blit(human, location)

    location = p.Rect(5*SQ_SIZE, 4*SQ_SIZE, SQ_SIZE, SQ_SIZE)
    screen.blit(computer, location)


def drawOptionWindow(screen, gs, human, computer) -> None:
    drawBoard(screen)
    drawOptionBox(screen, human, computer)


def OptionWindow(screen, gs) -> 0 | 1 | 2 :
    human = p.image.load("images/human.png")
    computer = p.image.load("images/computer.png")

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                return 0
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]/SQ_SIZE

                if row >= 4 and row <= 5.5 and col in [2, 5]:
                    return 1 if col == 2 else 2

        drawOptionWindow(screen, gs, human, computer)
        p.display.flip()


def main() -> None:
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
    flag = 1
    choice = 1
    while running:
        if flag:
            flag = 0
            choice = OptionWindow(screen, gs)
            if choice == 0:
                break
        for event in p.event.get():
            if not gs.whiteToMove and choice == 2:
                move = aimove(gs, 3)
                gs.makeMove(move)
                moveMade = True
                p.display.set_caption(turnText(gs.whiteToMove))
                print(len(gs.moveLog))
            if event.type == p.QUIT:
                running = False
            # mouse handel
            # mouse press
            elif event.type == p.MOUSEBUTTONDOWN and (gs.whiteToMove or choice == 1):
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
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:  # z to undo move
                    print(gs.moveLog)
                    gs.undoMove()
                    if not gs.whiteToMove and choice == 2:
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


def evaluate(gs)  :
    if gs.checkMate:
        if gs.whiteToMove:
            return -10000
        else:
            return 10000
    if gs.staleMate:
        return 0
    score = gs.boardscore
    if gs.whiteToMove:
        return score
    else:
        return -score


def minimaxalphabeta(gs, alpha, beta, depth) -> float :
    if(depth == 0):
        return evaluate(gs)
    maxscore = -10000
    moves = gs.getValidMove()
    moves.sort(key=ChessEngine.evalmove, reverse=True)
    for move in moves:
        if move.isPawnPromotion:
            move.promotionChoice = 'Q'
        gs.makeMove(move)
        score = -minimaxalphabeta(gs, -beta, -alpha, depth-1)
        gs.undoMove()
        if(score >= beta):
            return score
        if(score > maxscore):
            maxscore = score
        if(score > alpha):
            alpha = score
    return maxscore


def aimove(gs, depth) :
    machmove = None
    maxval = -99999
    alpha = -100000
    beta = 100000
    moves = gs.getValidMove()
    moves.sort(key=ChessEngine.evalmove, reverse=True)
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


def qsearch(gs, alpha, beta, depth):
    stndpt = evaluate(gs)
    if depth == 0:
        return stndpt
    if stndpt >= beta:
        return beta
    if alpha < stndpt:
        alpha = stndpt
    moves = gs.getValidMove()
    moves.sort(key=ChessEngine.evalmove, reverse=True)
    for move in moves:
        if move.pieceCaptured != '--':
            gs.makeMove(move)
            score = -qsearch(gs, -beta, -alpha, depth-1)
            gs.undoMove()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    return alpha


if __name__ == "__main__":
    main()
