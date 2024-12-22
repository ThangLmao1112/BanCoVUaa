from tkinter import *
from PIL import ImageTk
from chessboard import Board, ChessError, START_PATTERN
from tkinter import messagebox
class ChessGUI:
    pieces = {}  # Lưu trữ các quân cờ
    selected_piece = None  # Quân cờ đã chọn
    focused = None  # Các ô có thể di chuyển của quân cờ đã chọn
    rows = 8  # Số hàng
    columns = 8  # Số cột
    color1 = "#DDB88C"  # Màu của các ô sáng
    color2 = "#A66D4F"  # Màu của các ô tối
    dim_square = 64  # Kích thước của mỗi ô
    highlightcolor = "khaki"  # Màu nền của ô đang được chọn

    def __init__(self, parent, chessboard):
        """Khởi tạo giao diện người dùng cho trò chơi cờ vua."""
        self.parent = parent
        self.chessboard = chessboard

        # Khởi tạo menu
        self.menubar = Menu(parent)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New Game", command=self.new_game)  # Menu "New Game"
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.parent.config(menu=self.menubar)

        # Khởi tạo thông tin ở dưới cùng
        self.btmfrm = Frame(parent, height=64)
        self.info_label = Label(self.btmfrm, text="   Black to Start the Game", fg=self.color2)
        self.info_label.pack(side=RIGHT, padx=8, pady=5)
        self.btmfrm.pack(fill="x", side=BOTTOM)

        self.images = {}  # Lưu trữ hình ảnh quân cờ

        # Khởi tạo canvas vẽ bàn cờ
        canvas_width = self.columns * self.dim_square
        canvas_height = self.rows * self.dim_square
        self.canvas = Canvas(parent, width=canvas_width, height=canvas_height, background="grey")
        self.canvas.pack(padx=8, pady=8)

        self.draw_board()  # Vẽ bàn cờ
        self.draw_pieces()  # Vẽ các quân cờ
        self.canvas.bind("<Button-1>", self.square_clicked)  # Xử lý sự kiện khi nhấp vào ô cờ

    def new_game(self):
        """Khởi tạo lại bàn cờ và giao diện sau mỗi ván chơi mới."""
        self.chessboard.show(START_PATTERN)  # Hiển thị trạng thái khởi đầu
        self.draw_board()
        self.draw_pieces()
        self.info_label.config(text="Black to Start the Game", fg="red")  # Cập nhật thông tin

    def shift(self, p1, p2):
        """
        Xử lý nước đi và cập nhật thông tin hiển thị.
        p1: Vị trí ban đầu của quân cờ.
        p2: Vị trí đích đến.
        """
        piece = self.chessboard.get_piece(p1)  # Lấy quân cờ tại p1
        try:
            dest_piece = self.chessboard.get_piece(p2)
        except KeyError:  # Nếu vị trí đích không tồn tại
            dest_piece = None

        if dest_piece is None or dest_piece.color != piece.color:
            try:
                self.chessboard.shift(p1, p2)  # Thực hiện nước đi
            except self.chessboard.ChessError as error:
                # Hiển thị lỗi nếu nước đi không hợp lệ
                self.info_label.config(text=f"Error: {error.__class__.__name__}")
            else:
                # Cập nhật thông tin về lượt đi
                next_turn = "White" if piece.color == "black" else "Black"
                self.info_label.config(
                    text=f"{piece.color.capitalize()} moved {p1} to {p2}. {next_turn}'s turn."
                )

    def draw_board(self):
        """Vẽ bàn cờ với các ô màu sắc xen kẽ."""
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                self.draw_square(row, col, color)
                color = self.color1 if color == self.color2 else self.color2
        self.update_piece_positions()

    def draw_square(self, row, col, color):
        """Vẽ một ô trên bàn cờ."""
        x1 = (col * self.dim_square)
        y1 = ((7 - row) * self.dim_square)
        x2 = x1 + self.dim_square
        y2 = y1 + self.dim_square
        if self.focused and (row, col) in self.focused:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.highlightcolor, tags="area")  # Nổi bật ô
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="area")

    def update_piece_positions(self):
        """Cập nhật vị trí các quân cờ trên bàn cờ."""
        for name in self.pieces:
            piece_pos = self.pieces[name]
            x0 = (piece_pos[1] * self.dim_square) + int(self.dim_square / 2)
            y0 = ((7 - piece_pos[0]) * self.dim_square) + int(self.dim_square / 2)
            self.canvas.coords(name, x0, y0)  # Cập nhật tọa độ quân cờ
        self.canvas.tag_raise("occupied")  # Đưa quân cờ lên trên các ô
        self.canvas.tag_lower("area")  # Đưa ô xuống dưới

    def draw_pieces(self):
        """Vẽ tất cả các quân cờ lên bàn cờ."""
        self.canvas.delete("occupied")  # Xóa các quân cờ cũ
        for xycoord, piece in self.chessboard.items():
            x, y = self.chessboard.num_notation(xycoord)
            if piece is not None:
                self.create_piece_image(x, y, piece)

    def create_piece_image(self, x, y, piece):
        """Tạo hình ảnh cho quân cờ và đặt nó lên bàn cờ."""
        filename = f"pieces_image/{piece.shortname.lower()}{piece.color}.png"
        piece_name = f"{piece.shortname}{x}{y}"
        if filename not in self.images:
            self.images[filename] = ImageTk.PhotoImage(file=filename)

        self.canvas.create_image(0, 0, image=self.images[filename], tags=(piece_name, "occupied"), anchor="c")
        x0 = (y * self.dim_square) + int(self.dim_square / 2)
        y0 = ((7 - x) * self.dim_square) + int(self.dim_square / 2)
        self.canvas.coords(piece_name, x0, y0)

    def square_clicked(self, event):
        """Xử lý sự kiện khi nhấp vào ô cờ."""
        col_size = row_size = self.dim_square
        selected_column = event.x // col_size
        selected_row = 7 - (event.y // row_size)
        pos = self.chessboard.alpha_notation((selected_row, selected_column))

        if self.selected_piece:
            self.handle_move(self.selected_piece[1], pos)  # Di chuyển quân cờ
            self.selected_piece = None  # Hủy quân cờ đã chọn
            self.focused = None  # Hủy các ô có thể di chuyển
            self.pieces = {}  # Xóa các quân cờ cũ
            self.draw_board()  # Vẽ lại bàn cờ
            self.draw_pieces()  # Vẽ lại quân cờ

        self.focus(pos)  # Tạo hiệu ứng nổi bật cho quân cờ
        self.draw_board()  # Vẽ lại bàn cờ

    def handle_move(self, from_pos, to_pos):
        """Xử lý việc di chuyển quân cờ từ vị trí này sang vị trí khác."""
        piece = self.chessboard[from_pos]
        dest_piece = self.chessboard.get(to_pos, None)

        if dest_piece is None or dest_piece.color != piece.color:
            try:
                self.chessboard.shift(from_pos, to_pos)  # Thực hiện di chuyển
            except ChessError:
                pass

    def focus(self, pos):
        """Đánh dấu quân cờ đã chọn và làm nổi bật các nước đi có thể có của quân đó."""
        piece = self.chessboard.get(pos, None)
        if piece and piece.color == self.chessboard.player_turn:
            self.selected_piece = (piece, pos)  # Lưu quân cờ đã chọn
            self.focused = list(map(self.chessboard.num_notation, piece.moves_available(pos)))  # Lấy các ô có thể di chuyển

    

def main():
    root = Tk()
    root.title("Chess Game")
    board = Board()  # Khởi tạo bàn cờ
    gui = ChessGUI(root, board)  # Khởi tạo giao diện người dùng
    root.mainloop()

if __name__ == "__main__":
    main()
