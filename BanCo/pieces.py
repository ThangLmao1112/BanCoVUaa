import sys  

# Tạo lớp cha Piece
class Piece:  
    def __init__(self, color):  
        self.color = color  # Lưu màu
        self.shortname = self.shortname.lower() if color == 'black' else self.shortname.upper()

    def ref(self, board):  
        ''' Get a reference of chessboard instance '''  
        self.board = board  

# Tạo lớp con cho từng quân cờ
class King(Piece):  
    shortname = 'k'  

class Queen(Piece):  
    shortname = 'q'  

class Rook(Piece):  
    shortname = 'r'  

class Knight(Piece):  
    shortname = 'n'  

class Bishop(Piece):  
    shortname = 'b'  

class Pawn(Piece):  
    shortname = 'p'  

# Định nghĩa phương thức để trả về đối tượng quân cờ
SHORT_NAME = {  
    'R': 'Rook',  
    'N': 'Knight',  
    'B': 'Bishop',  
    'Q': 'Queen',  
    'K': 'King',  
    'P': 'Pawn'  
}  

def create_piece(piece, color='white'):  
    if piece in (None, ''):  
        return None  
    color = 'white' if piece.isupper() else 'black'  
    piece_name = SHORT_NAME[piece.upper()]  
    module = sys.modules[__name__]  
    return module.__dict__[piece_name](color)  # Tạo quân cờ dựa trên tên
