from scene import *
from ui import Path
from collections import Counter

# gobblet game

BSIZE = 4
ALL_HEIGHT = BSIZE + 2
MAX_HEIGHT = ALL_HEIGHT + 0.5
STACK_COUNT = 3
MAX_STACK_HEIGHT = 4


colors = {'B':'#3af', 'R':'#f00'}
darker_colors = {'B':'#259', 'R':'#900'}


def get_rect_pos(size, bounds):
    min_bound = min(bounds)
    piece_size = min_bound*(size+2)/(MAX_STACK_HEIGHT+2)
    #p_w = n_w*(size+2)//(MAX_STACK_HEIGHT+1)
    #p_h = n_h*(size+2)//(MAX_STACK_HEIGHT+1)
    return piece_size, piece_size


class Piece(ShapeNode):
    def __init__(self, color, size, pos, bounds, *args, **kwargs):
        ShapeNode.__init__(
            self,
            Path.rect(0, 0, *get_rect_pos(size, bounds)),
            colors[color],
            darker_colors[color],
            *args,
            **kwargs
        )
        self.cell_width, self.cell_height = bounds
        self.pos = pos
        self.return_to_pos()
        self.piece_color = color
        self.piece_size = size
        self.path.line_width = 12
    
    def get_x_pos(self, x_i):
        return (x_i + 0.5) * self.cell_width
    
    def get_y_pos(self, y_i):
        return (y_i + 0.5) * self.cell_height

    def can_move(self, piece):
        # can always move a piece to an empty space if right player
        if piece is None:
            return True
        # can only move to empty space from hand
        if self.pos[1] in (0, BSIZE + 1):
            return False
        if self.piece_size > piece.piece_size:
            return True
        return False
        
    def return_to_pos(self):
        self.run_action(Action.move_to(
            self.get_x_pos(self.pos[0]),
            self.get_y_pos(self.pos[1]),
            0.25,
            TIMING_LINEAR
        ))
        

    def move(self, slot, g_x, g_y):
        slot.append(self)
        self.pos = (g_x, g_y)
        self.return_to_pos()
        
        
class Cell(ShapeNode):
    def __init__(self, *args, **kwargs):
        ShapeNode.__init__(
            self,
            *args,
            **kwargs
        )
        self.contents = [None]
        
    #def __getitem__(self, index):
    #    return self.contents[index]
        
    def pop(self):
        return self.contents.pop()
        
    def peek(self):
        return self.contents[-1]
        
    def clear(self):
        self.contents = self.contents[:1]
    
    def append(self, item):
        self.contents.append(item)
        item.z_position = len(self.contents)
        

class Board(ShapeNode):
    def __init__(self, size, *args, **kwargs):
        self.width = size.width
        self.height = size.height * ALL_HEIGHT / MAX_HEIGHT
        ShapeNode.__init__(
            self,
            Path.rect(
                0,
                0,
                self.width,
                self.height,
            ),
            (1.0, 1.0, 0.0),
            *args,
            **kwargs
        )
        self.cell_width = self.width / BSIZE
        self.cell_height = self.height / ALL_HEIGHT
        self.cells = [
            [
                Cell(
                    Path.rect(0, 0, self.cell_width, self.cell_height),
                    'ff0' if (x + y) % 2 or y == 0 or y == BSIZE + 1 else 'dd0',
                    'aa0',
                    parent=self, position=(
                        self.cell_width * (x + 0.5),
                        self.cell_height * (y + 0.5)
                    )
                )
                for x in range(BSIZE)
            ]
            for y in range(ALL_HEIGHT)
        ]
        self.node_size = self.cell_width, self.cell_height
        
    def check_for_winner(self):
        for r in range(1, BSIZE+1):
            c = Counter(cell.peek().piece_color for cell in self.cells[r] if cell.peek())
            if c['R'] == BSIZE:
                return 'R'
            if c['B'] == BSIZE:
                return 'B'
        for c in range(BSIZE):
            l = [self.cells[r][c].peek() for r in range(1, BSIZE+1)]
            c = Counter(item.piece_color for item in l if item)
            if c['R'] == BSIZE:
                return 'R'
            if c['B'] == BSIZE:
                return 'B'
        l = [self.cells[i+1][i].peek() for i in range(BSIZE)]
        c = Counter(item.piece_color for item in l if item)
        if c['R'] == BSIZE:
            return 'R'
        if c['B'] == BSIZE:
            return 'B'
        l = [self.cells[BSIZE-i][i].peek() for i in range(BSIZE)]
        c = Counter(item.piece_color for item in l if item)
        if c['R'] == BSIZE:
            return 'R'
        if c['B'] == BSIZE:
            return 'B'
    
    def clear_board(self):
        for r in range(ALL_HEIGHT):
            for c in range(BSIZE):
                self.cells[r][c].clear()
    
    def reset(self):
        self.clear_board()
        LHI = ALL_HEIGHT - 1
        first_row = self.cells[0]
        last_row = self.cells[-1]
        for i in range(STACK_COUNT):
            first_row_cell = first_row[i]
            last_row_cell = last_row[i]
            for s in range(MAX_STACK_HEIGHT):
                first_row_cell.append(Piece(
                    'B', s, (i, 0), self.node_size,
                    parent=self, position = (self.width / 2, self.height / 2)
                ))
                last_row_cell.append(Piece(
                    'R', s, (i, LHI), self.node_size,
                    parent=self, position = (self.width / 2, self.height / 2)
                ))
    
    def __getitem__(self, index):
        return self.cells[index]

texts = {
    'R': "Red's turn",
    'B': "Blue's turn"
}

class Game(Scene):
    def setup(self):
        self.turn = 'R'
        self.root_node = Node(parent=self, position=(0, 0))
        self.background_color = '#fff'
        self.touch_start = None
        turn_font = ('monospace', 35)
        self.turn_label = LabelNode(texts[self.turn], font=turn_font, parent=self)
        self.turn_label.anchor_point = (0.5, 0)
        self.turn_label.position = (
            0.5 * self.bounds.width,
            self.bounds.height * ALL_HEIGHT / MAX_HEIGHT 
        )
        self.turn_label.color = colors[self.turn]
        self.board = Board(self.bounds, parent=self.root_node, anchor_point=(0, 0))
        self.selected = None
        self.reset()
        
    # TODO Support resizing
    def did_change_size(self):
        pass
        
    def reset(self):
        self.board.reset()
            
    def nextturn(self, winner):
        if (winner):
            self.turn = ''
            self.turn_label.color = colors[winner]
            self.turn_label.text = 'WIN!'
            return
        if self.turn == 'R':
            self.turn = 'B'
        else:
            self.turn = 'R'
        self.turn_label.color = colors[self.turn]
        self.turn_label.text = texts[self.turn]
        
    def get_touched_piece(self, loc):
        pos = self.board.point_from_scene(loc)
        x = int(pos[0] * BSIZE / self.board.width)
        y = int(pos[1] * ALL_HEIGHT / self.board.height)
        if x < 0 or y < 0 or x >= BSIZE or y >= ALL_HEIGHT:
            return None, -1, -1
        cell = self.board[y][x]
        if cell.frame.contains_point(pos):
            return cell.peek(), y, x
        return None, -1, -1
                    
    def run_warning_shake(self):
        self.root_node.run_action(Action.sequence(
            Action.move_to(0, 0, 0),
            Action.move_by(12, 0, 0.03, TIMING_BOUNCE_IN),
            Action.move_by(-24, 0, 0.06, TIMING_SINODIAL),
            Action.move_to(0, 0, 0.03, TIMING_BOUNCE_OUT)
        ))

    def touch_began(self, touch):        
        if self.turn == '':
            self.reset()
        if self.selected:
            return
        piece, gy, gx = self.get_touched_piece(touch.location)
        # make sure not to play from opposite hand
        if (gy == 0 or gy == BSIZE + 1) and piece is not None and piece.piece_color != self.turn:
            self.run_warning_shake()
            return
        if piece is None:
            self.run_warning_shake()
            return
        for r in range(1, BSIZE + 1):
            for c in range(BSIZE):
                if (r, c) == (gy, gx):
                    continue
                if piece.can_move(self.board[r][c].peek()):
                    self.selected = piece
                    self.touch_start = (gx, gy)
                    return

    def touch_moved(self, touch):
        if (self.selected is None):
            return
        x, y = self.board.point_from_scene(touch.location)
        #dx = touch.location[0] - touch.prev_location[0]
        #dy = touch.location[1] - touch.prev_location[1]
        self.selected.run_action(
            Action.move_to(x, y, 0)
        )

    def touch_ended(self, touch):
        if self.selected is None:
            return
        touched_piece, gy, gx = self.get_touched_piece(touch.location)
        if self.touch_start == (gx, gy):
            self.selected.return_to_pos()
            self.selected = None
            return
        if gy < 1 or gy > BSIZE:
            self.selected.return_to_pos()
            self.run_warning_shake()
            self.selected = None
            return
        sx, sy = self.touch_start
        if self.selected.can_move(touched_piece):
            self.board[sy][sx].pop()
            self.selected.move(
                self.board[gy][gx],
                gx,
                gy
            )
            winner = self.board.check_for_winner()
            self.nextturn(winner)
        else:
            self.run_warning_shake()
            self.selected.return_to_pos()
        self.selected = None

        
if __name__ == '__main__':
    run(Game())

#render()
