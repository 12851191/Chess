
import pygame
from pygame.constants import *
import ChessEngine
from Constants import *
import ChessAI

pygame.init()
pygame.mixer.init()


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK',
              'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']

    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(
            'images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


def main():
    pygame.init()
    icon = pygame.image.load('images/wN.png')
    caption = pygame.display.set_caption("AW Genuis Hour Project - Chess!")
    screen_icon = pygame.display.set_icon(icon)
    screen = pygame.display.set_mode(
        (BOARD_WIDTH + MOVE_LOG_PANAL_WIDTH, BOARD_HEIGHT))
    clock = pygame.time.Clock()
    gs = ChessEngine.Gamestate()
    validMoves = gs.getValidMoves()
    moveMade = False
    moveDone = True
    load_images()
    global pieceCapturedSound
    global pieceMovedSound
    global StartEndSound
    pieceCapturedSound = pygame.mixer.Sound('Sounds/Piece Captured.wav')
    pieceMovedSound = pygame.mixer.Sound('Sounds/Piece moved.wav')
    StartEndSound = pygame.mixer.Sound('Sounds/Start and End Sound.wav')
    running = True
    animation_feauture = True
    animate = False
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True
    playerTwo = False
    AIThinking = False
    choose = True
    music = True
    moveLogFont = pygame.font.SysFont('Arial', 16, True, False)

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (
            not gs.whiteToMove and playerTwo)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_z:
                    gs.undoMove()
                    if not playerTwo:
                        gs.undoMove()
                    animate = False
                    moveMade = True
                    gameOver = False

                if event.key == K_a:
                    animation_feauture = not animation_feauture
                if event.key == K_m:
                    music = not music

                if event.key == K_r:
                    gs = ChessEngine.Gamestate()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    moveDone = True
                    animate = False
                    music = True
                    animation_feauture = True
                    gameOver = False
                    choose = True
                if choose:
                    if event.key == K_y:
                        choose = False
                        playerTwo = False
                        pygame.mixer.Sound.play(StartEndSound)
                    elif event.key == K_n:
                        choose = False
                        playerTwo = True
                        pygame.mixer.Sound.play(StartEndSound)
                if not music:
                    pygame.mixer.Sound.set_volume(StartEndSound, 0.0)
                    pygame.mixer.Sound.set_volume(pieceCapturedSound, 0.0)
                    pygame.mixer.Sound.set_volume(pieceMovedSound, 0.0)
                else:
                    pygame.mixer.Sound.set_volume(StartEndSound, 1.0)
                    pygame.mixer.Sound.set_volume(pieceCapturedSound, 1.0)
                    pygame.mixer.Sound.set_volume(pieceMovedSound, 1.0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and not choose:
                    location = pygame.mouse.get_pos()

                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE

                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(
                            playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                moveDone = False
                                animate = True
                                print(move.getChessNotation())
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            if not gameOver and not humanTurn:
                if not AIThinking:
                    AIThinking = True

                    AIMove = ChessAI.findBestMove(gs, validMoves)
                    if AIMove is None:
                        AIMove = ChessAI.findRandomMove(validMoves)
                    gs.makeMove(AIMove)
                    moveMade = True
                    moveDone = False
                    animate = True
                    AIThinking = False
                    humanTurn = (gs.whiteToMove and playerOne) or (
                        not gs.whiteToMove and playerTwo)

            if moveMade:
                if animation_feauture:
                    if animate:
                        animateMove(gs.moveLog[-1],
                                    screen, gs.board, clock)
                validMoves = gs.getValidMoves()
                moveMade = False
                moveDone = True
                animate = False

        drawGameState(screen, gs, validMoves, sqSelected,
                      choose, moveLogFont, AIThinking)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, 'Black Wins by Checkmate')
            else:
                drawEndGameText(screen, 'White Wins by Checkmate')
        elif gs.stalemate:
            gameOver = True
            drawEndGameText(screen, 'Stalemate')

        clock.tick(FPS)
        pygame.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected, choose, moveLogFont, AIThinking):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected, AIThinking)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)
    if choose:
        font = pygame.font.SysFont('Helvitca', 32, True, False)
        textObject = font.render(
            'Do you want to play with an AI (y/n)?', 0, pygame.Color('Black'))
        textlocation = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
            BOARD_WIDTH//2 - textObject.get_width()//2, BOARD_HEIGHT//2 - textObject.get_height()//2)
        screen.blit(textObject, textlocation)


def drawBoard(screen):
    global colors
    colors = [pygame.Color(BOARD_LIGHT_COLOR), pygame.Color(BOARD_DARK_COLOR)]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], pygame.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    moveLogRect = pygame.Rect(
        BOARD_WIDTH, 0, MOVE_LOG_PANAL_WIDTH, MOVE_LOG_PANAL_HEIGHT)
    pygame.draw.rect(screen, pygame.Color('Dark Grey'), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 4
    padding = 5
    textY = 5
    lineSpacing = 2
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, pygame.Color('Black'))
        textlocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textlocation)
        textY += textObject.get_height() + lineSpacing
    if gs.checkmate:
        font = pygame.font.SysFont('Arial', 24, True, False)
        if gs.whiteToMove:
            textY += textObject.get_height() + lineSpacing
            textObject = font.render("0-1", True, pygame.Color('Black'))
            textlocation = moveLogRect.move(padding, textY)
            screen.blit(textObject, textlocation)
        else:
            textY += textObject.get_height() + lineSpacing
            textObject = font.render("1-0", True, pygame.Color('Black'))
            textlocation = moveLogRect.move(padding, textY)
            screen.blit(textObject, textlocation)
    elif gs.stalemate:
        font = pygame.font.SysFont('Arial', 24, True, False)
        textY += textObject.get_height() + lineSpacing
        textObject = font.render("1/2-1/2", True, pygame.Color('Black'))
        textlocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textlocation)


def highlightSquares(screen, gs, validMoves, sqSelected, AIThinking):
    if sqSelected != ():
        if AIThinking:
            r, c = sqSelected
            if gs.board[r][c][0] == 'w':
                gs.whiteToMove = not gs.whiteToMove
                validMoves = gs.getAllPossibleMoves()
                gs.whiteToMove = not gs.whiteToMove
                s = pygame.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(pygame.Color('light green'))
                screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
                s.fill(pygame.Color('dark green'))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        screen.blit(
                            s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
        else:
            r, c = sqSelected
            if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
                s = pygame.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(pygame.Color('blue'))
                screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
                s.fill(pygame.Color('yellow'))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        screen.blit(
                            s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

    if gs.inCheck():
        c = pygame.Surface((SQ_SIZE, SQ_SIZE))
        c.set_alpha(100)
        c.fill(pygame.Color('red'))
        if gs.whitKingInCheck:
            screen.blit(
                c, ((gs.whiteKingLocation[1])*SQ_SIZE, (gs.whiteKingLocation[0])*SQ_SIZE))
        elif gs.blackKingInCheck:
            screen.blit(
                c, ((gs.blackKingLocation[1])*SQ_SIZE, (gs.blackKingLocation[0])*SQ_SIZE))


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(dR)+abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount,
                move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pygame.Rect(move.endCol*SQ_SIZE,
                                move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + \
                    1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = pygame.Rect(
                    move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(
            c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(60)
    if move.pieceCaptured == '--':
        pygame.mixer.Sound.play(pieceMovedSound)
    else:
        pygame.mixer.Sound.play(pieceCapturedSound)


def drawEndGameText(screen, text):
    font = pygame.font.SysFont('Helvitca', 32, True, False)
    textObject = font.render(text, 0, pygame.Color('Black'))
    textlocation = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH//2 - textObject.get_width()//2, BOARD_HEIGHT//2 - textObject.get_height()//2)
    screen.blit(textObject, textlocation)
    textObject = font.render(text, 0, pygame.Color('Light Blue'))
    screen.blit(textObject, textlocation.move(-3, -3))


if __name__ == '__main__':
    main()
