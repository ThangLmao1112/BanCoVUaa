from tkinter import *
from PIL import ImageTk
from chessboard import Board

class GUI:
    rows = 8
    columns = 8
    color1 = "#DDB88C"  # Màu sắc ô 1
    color2 = "#A66D4F"  # Màu sắc ô 2
    dim_square = 64  # Kích thước ô

    def __init__(self, parent, chessboard):
        self.parent = parent
        self.chessboard = chessboard
        self.images = {}
        
        # Thiết lập kích thước canvas
        canvas_width = self.columns * self.dim_square
        canvas_height = self.rows * self.dim_square
        self.canvas = Canvas(
            parent,
            width=canvas_width,
            height=canvas_height,
            background="grey"
        )
        self.canvas.pack(padx=8, pady=8)
        self.draw_board()  # Vẽ bàn cờ
        self.draw_pieces()  # Vẽ quân cờ

    def draw_board(self):
        color = self.color2
        for r in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for c in range(self.columns):
                x1 = c * self.dim_square
                y1 = (7 - r) * self.dim_square
                x2 = x1 + self.dim_square
                y2 = y1 + self.dim_square
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, tags="area"
                )
                color = self.color1 if color == self.color2 else self.color2

    def draw_pieces(self): 
        self.canvas.delete("occupied")  # Xóa quân cờ cũ
        for xycoord, piece in self.chessboard.items():
            x, y = self.chessboard.num_notation(xycoord)
            if piece is not None:
                filename = "../BanCo/pieces_image/%s%s.png" % (piece.shortname.lower(), piece.color)
                piecename = "%s%s%s" % (piece.shortname, x, y)
                
                # Kiểm tra và tải hình ảnh
                if filename not in self.images:
                    self.images[filename] = ImageTk.PhotoImage(file=filename)
                
                # Vẽ quân cờ
                self.canvas.create_image(0, 0, image=self.images[filename], tags=(piecename, "occupied"), anchor="c")
                x0 = (y * self.dim_square) + int(self.dim_square / 2)
                y0 = ((7 - x) * self.dim_square) + int(self.dim_square / 2)
                self.canvas.coords(piecename, x0, y0)  # Đặt tọa độ cho quân cờ

def main():
    root = Tk()
    root.title("Cờ vua")
    board = Board()  # Khởi tạo bàn cờ
    gui = GUI(root, board)
    root.mainloop()  # Bắt đầu vòng lặp GUI

if __name__ == "__main__":
    main()
