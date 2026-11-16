#Imports
import sys
import chess
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PySide6.QtGui import QPixmap 
from PySide6.QtCore import Qt 
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
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
                selected_square = self.manager.squares[square_index]
                selected_square.setStyleSheet("background-color: #646e40;")
                self.manager.selected_square = square_index
                self.manager.highlight_legal_moves()
                
                
       
         else: 
           if friendly_piece:
               self.manager.reset_highlight()
               self.manager.clear_legal_moves()
               selected_square = self.manager.squares[square_index]
               selected_square.setStyleSheet("background-color: #646e40;")
               self.manager.selected_square = square_index
               self.manager.highlight_legal_moves()
               
           else:
               move = chess.Move(from_square = self.manager.selected_square, to_square= square_index)
               if move in self.manager.board.legal_moves:
                   self.manager.board.push(move)
                   self.manager.update_board()
                   self.manager.highlight_last_move()

               self.manager.reset_highlight()
               self.manager.clear_legal_moves()
               self.manager.selected_square = None

    def paintEvent(self, event):
        QLabel.paintEvent(self, event)
        if self.show_dot:
            painter = QPainter(self)
            fill_dot = QColor(0, 0, 0, 55)
            painter.setBrush(fill_dot)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(28, 28, 20, 20)
            painter.end()
        elif self.show_capture_ring:
            ring_color = QColor(0, 0, 0, 65)
            ring_pen = QPen(ring_color, 6)
            capture_ring = QPainter(self)
            capture_ring.setBrush(Qt.NoBrush)
            capture_ring.setPen(ring_pen)
            capture_ring.drawEllipse(5, 5, 65, 65)
            capture_ring.end()




class ChessBoard:
    def __init__(self):
        self.selected_square = None
        self.board = chess.Board()
        self.squares = {}

    def update_board(self):
        for square_index, square in self.squares.items():
            piece = self.board.piece_at(square_index)
            square.clear()
            if piece is not None:
                image_path = piece_images[piece.symbol()]
                image = QPixmap(image_path)
                if image.isNull():
                    print("ERROR FINDING IMAGE", image_path)
                else:
                    resized_image = image.scaled(65, 65)
                    square.setPixmap(resized_image)
                    square.setAlignment(Qt.AlignCenter)

    def reset_highlight(self):
        if self.selected_square is not None:
            previous_widget = self.squares[self.selected_square]
            if(previous_widget.row + previous_widget.col) % 2 == 0:
                previous_widget.setStyleSheet("background-color: #f0d9b5;")
            else:
                previous_widget.setStyleSheet("background-color: #b58863;")

    def highlight_legal_moves(self):
        for move in self.board.legal_moves:
            if move.from_square == self.selected_square:
                destination_widget = self.squares[move.to_square]
                destination_piece = self.board.piece_at(move.to_square)
                if destination_piece is not None:
                    destination_widget.show_capture_ring = True
                    destination_widget.show_dot = False
                else:
                    destination_widget.show_capture_ring = False
                    destination_widget.show_dot= True

                destination_widget.update()
                    
    def clear_legal_moves(self):
        for square_index, square in self.squares.items():
            square.show_dot = False
            square.show_capture_ring = False
            square.update()

    def highlight_last_move(self):
        if self.board.move_stack:
           last_move = self.board.peek()
           print(chess.square_name(last_move.from_square))
           print(chess.square_name(last_move.to_square))
            
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
        square.show_dot = False
        square.show_capture_ring = False
        if (row + col) % 2 == 0:
            square.setStyleSheet("background-color: #f0d9b5;")  
        else:
             square.setStyleSheet("background-color: #b58863;") 
       
        grid.addWidget(square, row, col)
        square_index = chess.square(col, 7 - row)
        board_manager.squares[square_index] = square


board_manager.update_board()
window.show()




#region Close Program
sys.exit(app.exec())
#endregion