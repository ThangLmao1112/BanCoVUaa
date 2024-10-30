import pieces  
import re  

# Tạo lớp Board
START_PATTERN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w 0 1'  

class Board(dict):  
    y_axis = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')  
    x_axis = (1, 2, 3, 4, 5, 6, 7, 8)  
  
    def __init__(self, patt=None):  
        self.process_notation(START_PATTERN)  # Khởi tạo bàn cờ với mẫu FEN

    def process_notation(self, patt):  
        self.clear()  
        patt = patt.split('/')  

        # Mở rộng khoản trắng 
        def expand_whitespaces(match):  
            return '' * int(match.group(0))  
        
        patt[0] = re.sub(r'\d', expand_whitespaces, patt[0])  
        
        for x, row in enumerate(patt[0].split('/')):  
            for y, alphabet in enumerate(row):  
                if alphabet == '':  
                    continue  
                xycoord = self.alpha_notation((7 - x, y))  
                self[xycoord] = pieces.create_piece(alphabet)  # Khởi tạo quân cờ  
                self[xycoord].ref(self)  
        
        self.player_turn = 'white' if patt[1] == 'w' else 'black'  # Lưu người chơi hiện tại

    def is_on_board(self, coord):  
        return 0 <= coord[0] < 8 and 0 <= coord[1] < 8 
        
    def alpha_notation(self, xycoord):  
        if not self.is_on_board(xycoord):  
            return  
        return self.y_axis[xycoord[1]] + str(self.x_axis[xycoord[0]])  

    def num_notation(self, xycoord):  
        return int(xycoord[1]) - 1, self.y_axis.index(xycoord[0])  

    def occupied(self, color):  
        return [coord for coord in self if self[coord].color == color]  # Lấy các vị trí đã chiếm bởi quân cùng màu

# Xử lý lỗi và ngoại lệ
class ChessError(Exception): pass
