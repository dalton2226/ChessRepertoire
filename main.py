#Imports
import sys, json
import chess
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton , QVBoxLayout, QHBoxLayout, QDialog, QListWidget, QLineEdit, QComboBox
from PySide6.QtGui import QPixmap 
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF
import math
app = QApplication(sys.argv)

#region Create Window
window = QWidget()
window.setWindowTitle("Chess Repertoire")
main_layout = QVBoxLayout()
grid = QGridLayout()
board_widget = QWidget()
window.setLayout(main_layout)
board_widget.setLayout(grid)
main_layout.addWidget(board_widget)
grid.setSpacing(0)
grid.setContentsMargins(0, 0, 0, 0)
main_layout.setAlignment(board_widget, Qt.AlignCenter)

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
                   print("Available repertoire moves:", self.manager.get_repertoire_continuations())
                   
               self.manager.reset_highlight()
               self.manager.clear_legal_moves()
               self.manager.selected_square = None
               self.manager.highlight_last_move()
               print(self.manager.get_recorded_moves())

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
        self.last_highlighted_move = None

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

    def restore_square_color(self, square_index):
        previous_widget = self.squares[square_index]
        if(previous_widget.row + previous_widget.col) % 2 == 0:
                previous_widget.setStyleSheet("background-color: #f0d9b5;")
        else:
            previous_widget.setStyleSheet("background-color: #b58863;")
                    
    def clear_legal_moves(self):
        for square_index, square in self.squares.items():
            square.show_dot = False
            square.show_capture_ring = False
            square.update()

    def highlight_last_move(self):
        if self.board.move_stack:
           if self.last_highlighted_move is not None:
               previous_from_widget = self.squares[self.last_highlighted_move.from_square]
               previous_to_widget = self.squares[self.last_highlighted_move.to_square]
            
               if (previous_from_widget.row + previous_from_widget.col) % 2 == 0:
                previous_from_widget.setStyleSheet("background-color: #f0d9b5;")
               else:
                previous_from_widget.setStyleSheet("background-color: #b58863;")
               if (previous_to_widget.row + previous_to_widget.col) % 2 ==0:
                   previous_to_widget.setStyleSheet("background-color: #f0d9b5;")
               else:
                   previous_to_widget.setStyleSheet("background-color: #b58863;")
                   
               
           last_move = self.board.peek() # board.peek Retrieves Most recent Move
           from_widget = self.squares[last_move.from_square]
           to_widget = self.squares[last_move.to_square]
           from_widget.setStyleSheet("background-color: #cdd26a;")
           to_widget.setStyleSheet("background-color: #cdd26a;")
           self.last_highlighted_move = last_move

    def undo_move(self):
            if self.board.move_stack:
                self.reset_highlight()
                self.clear_legal_moves()
                self.selected_square = None

                self.board.pop()
                self.update_board()

            if self.board.move_stack:
                self.highlight_last_move()
            else:
                if self.last_highlighted_move is not None:
                    self.restore_square_color(self.last_highlighted_move.from_square)
                    self.restore_square_color(self.last_highlighted_move.to_square)
                    self.last_highlighted_move = None

            print("Available repertoire moves:", self.get_repertoire_continuations())

    def save_opening(self, opening_name, opening_color):
        moves = self.get_recorded_moves()

        if not moves:
            print("No moves to save!")
            return


        opening = {
            "Name": opening_name,
            "Color": opening_color,
            "Lines": [moves]
            
        }

        openings = self.load_opening()
        for existing_opening in openings["Openings"]:
            if existing_opening["Name"] == opening_name and existing_opening["Color"] == opening_color:
                if moves not in existing_opening["Lines"]:
                    existing_opening["Lines"].append(moves)
                break
        else:
            openings["Openings"].append(opening)
                    


        with open("Openings.json", "w", encoding="utf-8") as file:
            json.dump(openings, file, indent=4)
        
        return True
    def load_opening(self):
        try:
            with open("Openings.json", "r") as file:
                openings = json.load(file)
            if "Openings" not in openings:
                openings = {"Openings": [openings]}

            return openings
        except FileNotFoundError:
            return {"Openings": []}

    def get_recorded_moves(self):
        moves = []

        for move in self.board.move_stack:
            moves.append(move.uci())

        return moves

    def show_save_window(self):
        dialog = QDialog()
        dialog.setWindowTitle("Save Opening")
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        opening_list = QListWidget()
        layout.addWidget(opening_list)
        name_input = QLineEdit()
        name_input.setPlaceholderText("New Opening")
        layout.addWidget(name_input)
        color_choice = QComboBox()
        color_choice.addItem("White")
        color_choice.addItem("Black")
        layout.addWidget(color_choice)
        create_opening_button = QPushButton("Create Opening")
        layout.addWidget(create_opening_button)

        def create_opening ():
            opening_name = name_input.text().strip()
            opening_color = color_choice.currentText()
            
            if not opening_name:
                print("Enter Opening Name")
                return
            
            saved = self.save_opening(opening_name, opening_color)
            if saved:
                dialog.accept()

            print("Creating Opening")
            print(opening_name)
            print(opening_color)


        create_opening_button.clicked.connect(create_opening)
        saved_openings = self.load_opening()

        for opening in saved_openings["Openings"]:
            opening_list.addItem(opening["Name"])
            
        def select_opening():
            selected_item = opening_list.currentItem()
            if selected_item is not None:
                selected_name = selected_item.text()

                for opening in saved_openings["Openings"]:
                    if opening["Name"] == selected_name:
                        selected_color = opening["Color"]
                        saved = self.save_opening(selected_name, selected_color)
                        if saved:  
                            dialog.accept()
                            break


        opening_list.itemDoubleClicked.connect(select_opening)

        dialog.exec()

    def get_repertoire_continuations(self):
        current_moves = self.get_recorded_moves()
        saved_openings = self.load_opening()
        continuations = set()
        
        for opening in saved_openings["Openings"]:
            for opening_moves in opening["Lines"]:
                if current_moves == opening_moves[:len(current_moves)]:
                    if len(opening_moves) > len(current_moves):
                        next_move = opening_moves[len(current_moves)]
                        continuations.add(next_move)
                        print("Matching opening:", opening["Name"])
                        print(next_move)
        return list(continuations)
                    
class ArrowOverlay(QWidget):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def square_to_pixels(self, square_index):
        column = chess.square_file(square_index)
        row = 7 - chess.square_rank(square_index)
        centerX = (column * 75) + 37.5
        centerY = (row * 75) + 37.5
        return centerX, centerY
        
        
        
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 150, 255, 180), 6)
        repertoire_moves = self.manager.get_repertoire_continuations()
        painter.setPen(pen)
        for uci_move in repertoire_moves:
            move = chess.Move.from_uci(uci_move)
            print (move.from_square, move.to_square)
            start_x, start_y = self.square_to_pixels(move.from_square)
            end_x, end_y = self.square_to_pixels(move.to_square)
            painter.drawLine(
                int(start_x),
                int(start_y),
                int(end_x),
                int(end_y)
            )
            dx = end_x - start_x
            dy = end_y - start_y
            length = math.hypot(dx, dy)
            if length > 0:
                ux = dx/length
                uy = dy/length
                base_x = end_x - ux * 20
                base_y = end_y - uy * 20
                perp_x = -uy
                perp_y = ux
                left_x = base_x + perp_x * 12
                left_y = base_y + perp_y * 12
                right_x = base_x - perp_x * 12
                right_y = base_y - perp_y * 12
                tip = QPointF(end_x,end_y)
                left_corner = QPointF(left_x,left_y)
                right_corner = QPointF(right_x, right_y)
                arrow = QPolygonF([tip,left_corner,right_corner])
                painter.setBrush(QColor(0, 150, 255, 180))
                painter.drawPolygon(arrow)

                #print(dx,dy,ux,uy,length,base_x,base_y,perp_x,perp_y,left_x,left_y,right_x,right_y)
        painter.end()


        

board_manager = ChessBoard()
print(board_manager.load_opening())

saved_openings = board_manager.load_opening()
for opening in saved_openings["Openings"]:
    print(opening["Name"])
    print(opening["Lines"])
    print(len(opening["Lines"]))

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
undo_button = QPushButton("Undo")
undo_button.clicked.connect(board_manager.undo_move)
arrow_overlay = ArrowOverlay(board_manager, board_widget)
arrow_overlay.setGeometry(0, 0, 600, 600)
arrow_overlay.raise_()
arrow_overlay.show()
save_opening_button = QPushButton("Save Opening")
save_opening_button.clicked.connect(board_manager.show_save_window)
load_opening_button = QPushButton("Load Opening")
load_opening_button.clicked.connect(board_manager.load_opening)
main_layout.addWidget(undo_button, alignment=Qt.AlignHCenter)
main_layout.addWidget(save_opening_button, alignment=Qt.AlignHCenter)
main_layout.addWidget(load_opening_button, alignment=Qt.AlignHCenter)


window.show()




#region Close Program
sys.exit(app.exec())
#endregion