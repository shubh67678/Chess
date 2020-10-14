import pygame as p
import ChessEngine
WIDTH = HEIGHT = 400
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


def drawGameState(screen, gs):
    drawBoard(screen)
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
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            # mouse handel
            elif event.type == p.MOUSEBUTTONDOWN:  # mouse press
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
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                    sqSelected = ()
                    playerClicks = []
            # key handel
            if event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    print("in")
                    gs.undoMove()
                    moveMade = True

        if moveMade == True:
            validMoves = gs.getValidMove()
            moveMade = False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
