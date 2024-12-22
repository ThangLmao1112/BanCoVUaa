import sys

class Piece:
    def __init__(self, color):
        self.color = color  # Màu quân cờ (đen hoặc trắng)
        self.board = None  # Bàn cờ, khởi tạo là None
        self.shortname = self.shortname.lower() if color == 'black' else self.shortname.upper()  # Chữ cái đại diện quân cờ (ví dụ: 'K' cho vua, 'Q' cho hậu)

    def place(self, board):
        """Gán bàn cờ cho quân cờ."""
        self.board = board

    def ref(self, board):
        """Cập nhật lại bàn cờ cho quân cờ."""
        self.board = board

    def moves_available(self, pos):
        """Hàm này phải được cài đặt ở các lớp con để tính toán nước đi hợp lệ của quân cờ."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    def _calculate_moves(self, pos, diagonal, orthogonal, distance):
        """Tính toán nước đi của quân cờ dựa trên loại quân và hướng đi."""
        board = self.board
        allowed_moves = []
        orthogonal_moves = ((-1, 0), (0, -1), (0, 1), (1, 0))  # Các hướng đi theo chiều dọc và ngang
        diagonal_moves = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # Các hướng đi chéo
        beginning_pos = board.num_notation(pos.upper())  # Chuyển đổi vị trí thành tọa độ trên bàn cờ

        directions = []
        if orthogonal and diagonal:
            directions = diagonal_moves + orthogonal_moves  # Cả hai hướng
        elif diagonal:
            directions = diagonal_moves  # Chỉ chéo
        elif orthogonal:
            directions = orthogonal_moves  # Chỉ dọc và ngang

        # Tính toán các nước đi hợp lệ
        for x, y in directions:
            collision = False
            for step in range(1, distance + 1):
                if collision:
                    break
                dest = (beginning_pos[0] + step * x, beginning_pos[1] + step * y)
                dest_notation = board.alpha_notation(dest)
                if dest_notation not in board.occupied('white') + board.occupied('black'):
                    allowed_moves.append(dest)
                elif dest_notation in board.occupied(self.color):
                    collision = True
                else:
                    allowed_moves.append(dest)
                    collision = True

        allowed_moves = filter(board.is_on_board, allowed_moves)  # Lọc ra các nước đi hợp lệ
        return list(map(board.alpha_notation, allowed_moves))  # Trả về các nước đi hợp lệ dưới dạng ký hiệu bàn cờ

class King(Piece):
    shortname = 'k'

    def moves_available(self, pos):
        return self._calculate_moves(pos, True, True, 1)  # Vua có thể di chuyển 1 ô theo mọi hướng (dọc, ngang, chéo)

class Queen(Piece):
    shortname = 'q'

    def moves_available(self, pos):
        return self._calculate_moves(pos, True, True, 8)  # Hậu có thể di chuyển 8 ô theo mọi hướng (dọc, ngang, chéo)

class Rook(Piece):
    shortname = 'r'

    def moves_available(self, pos):
        return self._calculate_moves(pos, False, True, 8)  # Xe có thể di chuyển 8 ô theo chiều dọc và ngang
    
class Bishop(Piece):
    shortname = 'b'

    def moves_available(self, pos):
        return self._calculate_moves(pos, True, False, 8)  # Tượng có thể di chuyển 8 ô theo hướng chéo

class Knight(Piece):
    shortname = 'n'

    def moves_available(self, pos):
        allowed_moves = []
        board = self.board
        beginning_pos = board.num_notation(pos.upper())
        piece = board.get(pos.upper())

        changes = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]  # Các nước đi hình chữ "L" của mã

        for x, y in changes:
            dest = (beginning_pos[0] + x, beginning_pos[1] + y)
            if board.alpha_notation(dest) not in board.occupied(piece.color):
                allowed_moves.append(dest)

        allowed_moves = filter(board.is_on_board, allowed_moves)  # Lọc ra các nước đi hợp lệ
        return list(map(board.alpha_notation, allowed_moves))  # Trả về các nước đi hợp lệ


class Pawn(Piece):
    shortname = 'p'

    def moves_available(self, pos):
        allowed_moves = []
        board = self.board
        piece = self

        direction, enemy = (1, 'black') if self.color == 'white' else (-1, 'white')  # Tốt di chuyển lên hoặc xuống tùy vào màu
        start_row = 1 if self.color == 'white' else 6  # Tốt có thể di chuyển 2 ô từ vị trí ban đầu
        prohibited = board.occupied('white') + board.occupied('black')  # Các ô đã bị chiếm
        beginning_pos = board.num_notation(pos.upper())

        forward = (beginning_pos[0] + direction, beginning_pos[1])
        if board.alpha_notation(forward) not in prohibited:
            allowed_moves.append(forward)

            if beginning_pos[0] == start_row:
                double_forward = (forward[0] + direction, forward[1])
                if board.alpha_notation(double_forward) not in prohibited:
                    allowed_moves.append(double_forward)

        # Tính toán các nước đi tấn công (chéo)
        for a in [-1, 1]:
            attack = (beginning_pos[0] + direction, beginning_pos[1] + a)
            if board.alpha_notation(attack) in board.occupied(enemy):
                allowed_moves.append(attack)

        allowed_moves = filter(board.is_on_board, allowed_moves)  # Lọc ra các nước đi hợp lệ
        return list(map(board.alpha_notation, allowed_moves))  # Trả về các nước đi hợp lệ

# Từ điển ánh xạ tên quân cờ viết tắt sang tên đầy đủ
SHORT_NAME = {
    'R': 'Rook',  # Xe
    'N': 'Knight',  # Mã
    'B': 'Bishop',  # Tượng
    'Q': 'Queen',  # Hậu
    'K': 'King',  # Vua
    'P': 'Pawn'  # Tốt
}

def create_piece(piece, color='white'):
    """Tạo một đối tượng quân cờ dựa trên tên viết tắt và màu sắc."""
    if piece in (None, ''):
        return None  # Nếu không có quân cờ, trả về None
    color = 'white' if piece.isupper() else 'black'  # Xác định màu quân cờ
    piece_name = SHORT_NAME.get(piece.upper())  # Lấy tên đầy đủ của quân cờ từ từ điển SHORT_NAME
    module = sys.modules[__name__]  # Lấy module hiện tại
    return module.__dict__[piece_name](color)  # Trả về đối tượng quân cờ
