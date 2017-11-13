# gobblet game

WIDTH = 4
HEIGHT = 4
AH = HEIGHT + 2
STACKS = 3
STACKH = 4
WWIDTH = 320
CWIDTH = WWIDTH//WIDTH
CHEIGHT = CWIDTH
BHEIGHT = CHEIGHT*AH
WHEIGHT = BHEIGHT + 50
assert WWIDTH % WIDTH == 0

import pygame
from pygame import image

class Piece:
    def __init__(self, colour, size, pos):
        self.colour = colour
        self.size = size
        self.pos = pos

    def canmove(self, piece, turn):
        if piece is None:
            if self.colour == turn:
                return True
            return False
        if self.size > piece.size and self.pos != piece.pos:
            return True

    def move(self, pos):
        r, c = self.pos = pos
        board[r][c].append(self)

pygame.init()
colours = {'B':(29, 0, 255), 'R':(255, 0 ,0)}
myfont = pygame.font.SysFont("monospace", 15)
turns = {'R':(myfont.size("Red's turn"),
              myfont.render("Red's turn", True, colours['R'])),
         'B':(myfont.size("Blue's turn"),
              myfont.render("Blue's turn", True, colours['B']))}

def reset():
    global board
    board = [[[None] for c in range(WIDTH)] for r in range(AH)]
    LHI = AH - 1
    for i in range(STACKS):
        board[0][i] = [None] + [Piece('B', s, (0, i)) for s in range(STACKH)]
        board[LHI][i] = [None] + [Piece('R', s, (LHI, i)) for s in range(STACKH)]


reset()
selected = None
turn = 'R'

def nextturn():
    global turn
    if turn == 'R':
        turn = 'B'
    else:
        turn = 'R'

def render():
    window.fill((255, 255, 255))
    for r in range(AH):
        for c in range(WIDTH):
            piece = board[r][c][-1]
            if 1 <= r <= HEIGHT:
                pygame.draw.rect(window, (0, 0, 0), (c*CWIDTH, r*CHEIGHT,
                                                     CHEIGHT, CWIDTH), 1)
            if piece:
                pr, pc = piece.pos
                colour = piece.colour
                size = piece.size
                pw = CWIDTH*(size+2)//(STACKH+1)
                ph = CHEIGHT*(size+2)//(STACKH+1)
                pr = pr*CHEIGHT + (CWIDTH - pw)/2
                pc = pc*CWIDTH + (CHEIGHT - ph)/2
                pygame.draw.rect(window, colours[colour], (pc, pr, ph, pw))
    if selected:
        pc, pr = pygame.mouse.get_pos()
        colour = selected.colour
        size = selected.size
        pw = CWIDTH*(size+2)//(STACKH+1)
        ph = CHEIGHT*(size+2)//(STACKH+1)
        pr -= ph/2
        pc -= pw/2
        pygame.draw.rect(window, colours[colour], (pc, pr, pw, ph))
    size, text = turns[turn]
    tw, th = size
    offset = (50-th) // 2
    window.blit(text, (offset, BHEIGHT + offset))
    pygame.display.flip()

window = pygame.display.set_mode((WWIDTH, WHEIGHT))
render()

while True:
    update_required = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if y > BHEIGHT:
                continue
            gx = x*WIDTH//WWIDTH
            gy = y*AH//BHEIGHT
            piece = board[gy][gx][-1]
            if selected:
                if 1 <= gy <= HEIGHT:
                    if (gy, gx) != selected.pos and \
                       selected.canmove(piece, turn):
                        selected.move((gy, gx))
                        selected = None
                        nextturn()
                        update_required = True
            else:
                if piece is None:
                    continue
                else:
                    if piece.colour != turn and (r == 0 or r == AH - 1):
                        continue
                    for r in range(1, HEIGHT + 1):
                        for c in range(WIDTH):
                            if (r, c) == (gy, gx):
                                continue
                            if piece.canmove(board[r][c][-1], turn):
                                break
                        else:
                            continue
                        break
                    else:
                        continue
                    selected = piece
                    board[gy][gx].pop()
                    update_required = True
        if event.type == pygame.KEYDOWN:
            # keypress handling
            if event.key == pygame.K_r:
                reset()
                update_required = True
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                break
    else:
        if selected or update_required:
            render()
        continue
    break
