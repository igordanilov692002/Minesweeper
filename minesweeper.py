import itertools
import random


class Minesweeper():
    def __init__(self, height=8, width=8, mines=8):

        self.height = height
        self.width = width
        self.mines = set()

        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        count = 0

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        return self.mines_found == self.mines


class Sentence():
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        try:
            self.cells.remove(cell)
            self.count -= 1
        except Exception:
            pass

    def mark_safe(self, cell):
        try:
            self.cells.remove(cell)
        except Exception:
            pass


class MinesweeperAI():
    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
        self.safes_will_make = set()

        # List of sentences about the game known to be true
        self.knowledge: list[Sentence] = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def nearst_cells(self, cell):
        st = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.width and 0 <= j < self.height and not any((i, j) == x for x in self.moves_made):
                    st.add((i, j))
        return st

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)
        try:
            self.safes_will_make.remove(cell)
        except KeyError:
            pass
        nearst_cells = self.nearst_cells(cell)
        if count == 0:
            for i in nearst_cells:
                self.mark_safe(i)
                self.safes_will_make.add(i)
            return
        lst_new_knowledge = []
        flag = 1
        self.knowledge = self.clean_knowledge()
        for i in self.knowledge:
            if i.cells.issubset(nearst_cells) or nearst_cells.issubset(i.cells):
                flag = 0
                new_set = i.cells.difference(nearst_cells) if i.count > count else nearst_cells.difference(i.cells)
                new_count = abs(i.count - count)
                if new_count == 0:
                    for j in new_set:
                        self.mark_safe(j)
                        self.safes_will_make.add(j)
                if len(new_set) == new_count:
                    for j in new_set:
                        self.mark_mine(j)
                elif new_count > 0:
                    lst_new_knowledge.append(Sentence(new_set, new_count))
            elif len(i.cells) == i.count: # исправить
                lst_of_changes_mines = []
                for j in i.cells:
                    lst_of_changes_mines.append(j)
                for j in lst_of_changes_mines:
                    self.mark_mine(j)
            elif i.count == 0: # исправить
                lst_of_free_cells = []
                for j in i.cells:
                    self.safes_will_make.add(j)
                    lst_of_free_cells.append(j)
                for j in lst_of_free_cells:
                    self.mark_safe(j)
        if flag:
            self.knowledge.append(Sentence(nearst_cells, count))
        self.knowledge.extend(lst_new_knowledge)

    def clean_knowledge(self):
        lst = []
        for i in self.knowledge:
            if len(i.cells) != 0:
                lst.append(i)
        return lst



    def make_safe_move(self):
        if len(self.safes_will_make) == 0:
            return None
        cell = random.choice(list(self.safes_will_make))
        return cell

    def make_random_move(self, k=0):
        if k > 10:
            return None
        i, j = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        if (i, j) not in self.moves_made and (i, j) not in self.mines:
            return (i, j)
        else:
            k += 1
            return self.make_random_move(k)
