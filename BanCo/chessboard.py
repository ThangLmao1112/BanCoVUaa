import pieces
import re
from copy import deepcopy
# Định dạng ban đầu của bàn cờ (FEN notation)
START_PATTERN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR 0 0 1'

# Các ngoại lệ tùy chỉnh
class ChessError(Exception): pass
class Check(ChessError): pass
class InvalidMove(ChessError): pass
class CheckMate(ChessError): pass
class Draw(ChessError): pass
class NotYourTurn(ChessError): pass

# Lớp Bàn cờ
class Board(dict):
    # Trục x và y của bàn cờ
    y_axis = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')  
    x_axis = (1, 2, 3, 4, 5, 6, 7, 8)  

    # Các thuộc tính về trạng thái của trò chơi
    captured_pieces = {'white': [], 'black': []}
    player_turn = None  # Lượt đi của người chơi
    halfmove_clock = 0  # Đồng hồ nửa nước
    fullmove_number = 1  # Số lần đi đầy đủ
    history = []  # Lịch sử các nước đi

    def __init__(self, patt=None):  
        self.process_notation(START_PATTERN)  # Khởi tạo bàn cờ từ FEN notation

    # Phương thức xử lý và thiết lập trạng thái bàn cờ từ FEN notation
    def process_notation(self, patt):  
        """Xử lý FEN notation và thiết lập bàn cờ.""" 
        self.clear()  # Xóa bàn cờ hiện tại
        rows = patt.split('/')  # Tách các hàng trên bàn cờ

        # Hàm mở rộng các khoảng trắng theo số lượng
        def expand_whitespaces(match):  
            return ' ' * int(match.group(0))  

        # Mở rộng các ký tự số thành khoảng trắng
        expanded_rows = [re.sub(r'\d', expand_whitespaces, row) for row in rows[:8]]  

        # Đặt các quân cờ lên bàn theo FEN notation
        for x, row in enumerate(expanded_rows):  
            for y, alphabet in enumerate(row):  
                if alphabet == ' ':  
                    continue  
                xycoord = self.alpha_notation((7 - x, y))  # Chuyển đổi tọa độ từ số sang ký tự
                self[xycoord] = pieces.create_piece(alphabet)  # Tạo quân cờ
                if self[xycoord] is not None:
                    self[xycoord].ref(self)  # Tham chiếu quân cờ vào bàn cờ

        # Thiết lập lượt đi của người chơi
        self.player_turn = 'white' if patt.split()[1] == 'w' else 'black'

    # Kiểm tra tọa độ có nằm trên bàn cờ không
    def is_on_board(self, coord):  
        return 0 <= coord[0] < 8 and 0 <= coord[1] < 8 
        
    # Chuyển đổi tọa độ số thành ký tự (ví dụ: (7, 0) -> 'A1')
    def alpha_notation(self, xycoord):  
        if not self.is_on_board(xycoord):  
            return  
        return self.y_axis[xycoord[1]] + str(self.x_axis[xycoord[0]])  

    # Chuyển đổi tọa độ ký tự thành tọa độ số (ví dụ: 'A1' -> (7, 0))
    def num_notation(self, xycoord):  
        return int(xycoord[1]) - 1, self.y_axis.index(xycoord[0])  

    # Các phương thức xử lý quân cờ và nước đi
    def occupied(self, color):  
        return [coord for coord in self if self[coord].color == color]  # Các quân cờ của một màu

    def all_moves_available(self, color):
        result = []  
        # Duyệt qua tất cả các quân cờ của người chơi
        for coord in self.keys():  
            if self[coord] is not None and self[coord].color == color:  
                moves = self[coord].moves_available(coord)  # Lấy các nước đi hợp lệ
                if moves:  
                    result += moves  
        return result

    def position_of_king(self, color):
        # Tìm vị trí của quân vua
        for pos in self.keys():  
            if isinstance(self[pos], pieces.King) and self[pos].color == color:  
                return pos

    def king_in_check(self, color):
        # Kiểm tra xem vua có bị chiếu không
        king_pos = self.position_of_king(color)  
        opponent = 'black' if color == 'white' else 'white'  
        for piece in self.values():  
            if isinstance(piece, pieces.Piece) and king_pos in self.all_moves_available(opponent):  
                return True  
        return False

    def is_in_check_after_move(self, p1, p2):
        # Kiểm tra nếu quân cờ di chuyển có khiến vua bị chiếu hay không
        temp_board = deepcopy(self)  # Tạo bản sao bàn cờ
        temp_board.move(p1, p2)  # Di chuyển quân cờ
        return temp_board.king_in_check(self[p1].color)  # Kiểm tra vua có bị chiếu không

    def shift(self, p1, p2):
        p1, p2 = p1.upper(), p2.upper()  # Chuyển về chữ hoa để thống nhất
        piece = self[p1]  
        try:  
            dest = self[p2]  # Lấy quân cờ đích
        except KeyError:  
            dest = None  

        if self.player_turn != piece.color:  
            raise NotYourTurn(f"Not {piece.color}'s turn!")  # Kiểm tra lượt đi của người chơi

        enemy = 'white' if piece.color == 'black' else 'black'  
        moves_available = piece.moves_available(p1)  # Lấy các nước đi hợp lệ của quân cờ

        if p2 not in moves_available:  
            raise InvalidMove("Invalid move")  # Nước đi không hợp lệ

        if self.all_moves_available(enemy) and self.is_in_check_after_move(p1, p2):  
            raise Check("Move leaves king in check")  # Nước đi khiến vua bị chiếu

        if not moves_available and self.king_in_check(piece.color):  
            raise CheckMate("Player's king is in checkmate")  # Nếu không có nước đi và vua bị chiếu, thua

        elif not moves_available:  
            raise Draw("Stalemate: No valid moves available")  # Hòa vì không có nước đi hợp lệ


        else:  
            self.move(p1, p2)  # Di chuyển quân cờ
            self.complete_move(piece, dest, p1, p2)  # Hoàn tất nước đi

        

        
    def move(self, p1, p2):
        # Di chuyển quân cờ từ p1 đến p2
        piece = self[p1]  
        try:  
            dest = self[p2]  # Lấy quân cờ đích
        except KeyError:  
            dest = None  
        del self[p1]  # Xóa quân cờ tại p1
        self[p2] = piece  # Đặt quân cờ tại p2

    def complete_move(self, piece, dest, p1, p2):
        # Hoàn tất quá trình nước đi
        enemy = 'white' if piece.color == 'black' else 'black'  
        if piece.color == 'black':  
            self.fullmove_number += 1  # Tăng số lần đi đầy đủ
        self.halfmove_clock += 1  # Tăng đồng hồ nước rưỡi
        self.player_turn = enemy  # Chuyển lượt người chơi

        abbr = piece.shortname  # Lấy ký tự viết tắt của quân cờ
        if abbr == 'P':  
            abbr = ''  # Nếu là tốt thì không ghi chữ 'P'
            self.halfmove_clock = 0  # Reset đồng hồ nếu là tốt

        movetext = abbr + ('x' if dest else '') + p2.lower()  # Ghi lại nước đi
        if dest is None:  
            self.halfmove_clock = 0  # Reset đồng hồ nếu không có quân bị ăn
        self.history.append(movetext)  # Thêm vào lịch sử các nước đi

    # Hiển thị trạng thái bàn cờ
    def show(self, pat):
        self.clear()  # Xóa bàn cờ hiện tại
        pat = pat.split(' ')  # Tách FEN notation ra

        # Hàm mở rộng khoảng trắng
        def expand(match): return ' ' * int(match.group(0))
        pat[0] = re.compile(r'\d').sub(expand, pat[0])

        # Đặt các quân cờ lên bàn cờ từ FEN notation
        for x, row in enumerate(pat[0].split('/')):
            for y, letter in enumerate(row):
                if letter == ' ':
                    continue
                coord = self.alpha_notation((7 - x, y))  # Chuyển đổi tọa độ từ số sang ký tự
                self[coord] = pieces.create_piece(letter)  # Tạo quân cờ
                self[coord].place(self)  # Đặt quân cờ lên bàn

        # Thiết lập lại các thông số trò chơi
        self.player_turn = 'white' if pat[1] == 'w' else 'black'
        self.halfmove_clock = int(pat[2])
        self.fullmove_number = int(pat[3])

        
