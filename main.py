#Imports
import sys
import chess
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PySide6.QtGui import QPixmap 
from PySide6.QtCore import Qt
app = QApplication(sys.argv)

#region Create Window
window = QWidget()
window.setWindowTitle("Chess Repertoire")
grid = QGridLayout()
grid.setSpacing(0)
grid.setContentsMargins(0, 0, 0, 0)
window.setLayout(grid)
#endregion


class ChessSquare(QLabel):
    def mousePressEvent(self, event):
         square_index = chess.square(self.col, 7 - self.row)
         piece = self.manager.board.piece_at(square_index)
         friendly_piece = piece is not None and piece.color == self.manager.board.turn

         if self.manager.selected_square is None:
             if friendly_piece:
                self.manager.selected_square = square_index
         else: 
           if friendly_piece:
               print("Selected:", chess.square_name(square_index))
               self.manager.selected_square = square_index
           else:
               move = chess.Move(from_square = self.manager.selected_square, to_square= square_index)
               if move in self.manager.board.legal_moves:
                   print("Legal Move")
                   self.manager.board.push(move)
                   print(self.manager.board)
               else:
                   print("Illegal Move")
               self.manager.selected_square = None
               print(move)
                

        
class ChessBoard:
    def __init__(self):
        self.selected_square = None
        self.board = chess.Board()
        self.squares = {}

    def update_board(self):
        for square_index, square in self.squares.items():
            print(chess.square_name(square_index))

board_manager = ChessBoard()
print(board_manager.selected_square)
print(board_manager.board.turn)

#region Piece Images  
piece_images = {
    "P": "Assets/Pieces/wP.svg",
    "K": "Assets/Pieces/wK.svg",
    "N": "Assets/Pieces/wN.svg",
    "B": "Assets/Pieces/wB.svg",
    "R": "Assets/Pieces/wR.svg",
    "Q": "Assets/Pieces/wQ.svg",
    "p": "Assets/Pieces/bP.svg",
    "k": "Assets/Pieces/bK.svg",
    "n": "Assets/Pieces/bN.svg",
    "b": "Assets/Pieces/bB.svg",
    "r": "Assets/Pieces/bR.svg",
    "q": "Assets/Pieces/bQ.svg",

}
#endregion
for row in range(8):
    for col in range(8):
        square = ChessSquare()
        square.row = row
        square.col = col
        square.manager = board_manager
        square.setFixedSize(75, 75)
        if (row + col) % 2 == 0:
            square.setStyleSheet("background-color: #DEE3E6;")  
        else:
             square.setStyleSheet("background-color: #475569;") 
       
        grid.addWidget(square, row, col)
        square_index = chess.square(col, 7 - row)
        board_manager.squares[square_index] = square
        piece = board_manager.board.piece_at(square_index)
        if piece is not None:
            image_path = piece_images[piece.symbol()]
            image = QPixmap(image_path)
            if image.isNull():
                print("ERROR FINDING IMAGE", image_path)
            else:
                resized_image = image.scaled(65, 65)
                square.setPixmap(resized_image)
                square.setAlignment(Qt.AlignCenter)


board_manager.update_board()
window.show()




#region Close Program
sys.exit(app.exec())
#endregion