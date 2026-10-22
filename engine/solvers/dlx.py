"""
Sudoku Quest - Dancing Links (DLX) Exact Cover Solver
Implements Donald Knuth's Algorithm X using circular 4-way doubly linked lists (Dancing Links).
Converts 9x9 Sudoku into an exact cover problem with 729 choices and 324 constraints.
"""
import time
from typing import Optional, List, Tuple
from engine.solvers.base_solver import BaseSolver, SolverResult
from engine.models.board import Board
from core.constants import GRID_SIZE, CANONICAL_CELL_COUNT, TOTAL_CONSTRAINTS_9X9

class DLXNode:
    """Internal node in the Dancing Links toroidal linked matrix."""
    def __init__(self, col_node: Optional["ColumnNode"] = None, info: Optional[Tuple[int, int, int]] = None):
        self.left: "DLXNode" = self
        self.right: "DLXNode" = self
        self.up: "DLXNode" = self
        self.down: "DLXNode" = self
        self.col: Optional["ColumnNode"] = col_node
        self.info: Optional[Tuple[int, int, int]] = info  # (row, col, digit)

class ColumnNode(DLXNode):
    """Header node for a constraint column tracking column size."""
    def __init__(self, name: str):
        super().__init__(col_node=self)
        self.name: str = name
        self.size: int = 0

class DLXSolver(BaseSolver):
    """Exact Cover Solver using Knuth's Dancing Links Algorithm X."""

    def __init__(self, timeout_seconds: float = 5.0):
        super().__init__(timeout_seconds=timeout_seconds)

    def _build_matrix(self) -> Tuple[ColumnNode, List[List[DLXNode]]]:
        """Construct the 324-column exact cover matrix for standard 9x9 Sudoku."""
        root = ColumnNode("root")
        columns: List[ColumnNode] = []
        last_col = root

        # 324 Constraints:
        # 0..80: Cell (r, c) filled
        # 81..161: Row r has digit d
        # 162..242: Col c has digit d
        # 243..323: Box b has digit d
        for i in range(TOTAL_CONSTRAINTS_9X9):
            col = ColumnNode(f"C_{i}")
            col.left = last_col
            last_col.right = col
            last_col = col
            columns.append(col)

        root.left = last_col
        last_col.right = root

        # Store rows indexed by (r, c, d)
        all_rows: List[List[DLXNode]] = []

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b = (r // 3) * 3 + (c // 3)
                for d in range(1, 10):
                    digit_idx = d - 1
                    # 4 constraint column indices
                    c1 = r * 9 + c
                    c2 = 81 + r * 9 + digit_idx
                    c3 = 162 + c * 9 + digit_idx
                    c4 = 243 + b * 9 + digit_idx

                    col_indices = [c1, c2, c3, c4]
                    row_nodes: List[DLXNode] = []
                    info = (r, c, d)

                    for c_idx in col_indices:
                        col_hdr = columns[c_idx]
                        node = DLXNode(col_node=col_hdr, info=info)
                        # Link vertically into column
                        node.down = col_hdr
                        node.up = col_hdr.up
                        col_hdr.up.down = node
                        col_hdr.up = node
                        col_hdr.size += 1
                        row_nodes.append(node)

                    # Link horizontally within row
                    for k in range(4):
                        row_nodes[k].right = row_nodes[(k + 1) % 4]
                        row_nodes[(k + 1) % 4].left = row_nodes[k]

                    all_rows.append(row_nodes)

        return root, all_rows

    def _cover(self, col: ColumnNode) -> None:
        """Cover a constraint column: unlink it from header row and unlink rows in it."""
        col.right.left = col.left
        col.left.right = col.right

        i = col.down
        while i != col:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.col.size -= 1
                j = j.right
            i = i.down

    def _uncover(self, col: ColumnNode) -> None:
        """Uncover a constraint column: restore vertical and horizontal links."""
        i = col.up
        while i != col:
            j = i.left
            while j != i:
                j.col.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up

        col.right.left = col
        col.left.right = col

    def solve(self, board: Board) -> SolverResult:
        """Solve board using DLX."""
        start_ts = time.perf_counter()
        self.steps = 0
        root, _ = self._build_matrix()

        # Apply given clues on board
        initial_solution = []
        covered_cols: List[ColumnNode] = []

        # Find row nodes matching given digits
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = board.get_value(r, c)
                if val != 0:
                    initial_solution.append((r, c, val))
                    # Locate and cover matching node
                    b = (r // 3) * 3 + (c // 3)
                    digit_idx = val - 1
                    cell_col_idx = r * 9 + c

                    # Find cell column
                    curr = root.right
                    target_col = None
                    while curr != root:
                        if curr.name == f"C_{cell_col_idx}":
                            target_col = curr
                            break
                        curr = curr.right

                    if target_col and target_col.size > 0:
                        # Find row with digit
                        row_match = None
                        node = target_col.down
                        while node != target_col:
                            if node.info == (r, c, val):
                                row_match = node
                                break
                            node = node.down

                        if row_match:
                            self._cover(row_match.col)
                            covered_cols.append(row_match.col)
                            j = row_match.right
                            while j != row_match:
                                self._cover(j.col)
                                covered_cols.append(j.col)
                                j = j.right
                        else:
                            # Contradiction in given clues
                            return SolverResult(
                                solved=False,
                                elapsed_ms=(time.perf_counter() - start_ts) * 1000.0,
                                steps=0,
                                solutions_count=0
                            )

        solutions = []

        def search():
            self.steps += 1
            if time.perf_counter() - start_ts > self.timeout_seconds:
                return

            if root.right == root:
                # All constraints satisfied
                solutions.append(list(current_solution))
                return

            # S-Heuristic: choose column with minimum remaining choices
            min_col = None
            min_size = 999999
            c = root.right
            while c != root:
                if c.size < min_size:
                    min_size = c.size
                    min_col = c
                c = c.right

            if min_col is None or min_size == 0:
                return

            self._cover(min_col)

            r_node = min_col.down
            while r_node != min_col:
                current_solution.append(r_node.info)
                j = r_node.right
                while j != r_node:
                    self._cover(j.col)
                    j = j.right

                search()
                if len(solutions) >= 1:
                    # Found at least one solution
                    j = r_node.left
                    while j != r_node:
                        self._uncover(j.col)
                        j = j.left
                    current_solution.pop()
                    self._uncover(min_col)
                    return

                j = r_node.left
                while j != r_node:
                    self._uncover(j.col)
                    j = j.left

                current_solution.pop()
                r_node = r_node.down

            self._uncover(min_col)

        current_solution = list(initial_solution)
        search()

        elapsed = (time.perf_counter() - start_ts) * 1000.0

        if solutions:
            solved_board = board.clone()
            for r, c, d in solutions[0]:
                solved_board.cells[r][c].value = d
            return SolverResult(
                solved=True,
                solution=solved_board,
                elapsed_ms=elapsed,
                steps=self.steps,
                solutions_count=len(solutions),
                solutions=[solved_board]
            )

        return SolverResult(
            solved=False,
            solution=None,
            elapsed_ms=elapsed,
            steps=self.steps,
            solutions_count=0
        )

    def count_solutions(self, board: Board, max_count: int = 2) -> int:
        """Count distinct solutions up to max_count using DLX."""
        start_ts = time.perf_counter()
        root, _ = self._build_matrix()

        # Cover given clues
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = board.get_value(r, c)
                if val != 0:
                    cell_col_idx = r * 9 + c
                    curr = root.right
                    target_col = None
                    while curr != root:
                        if curr.name == f"C_{cell_col_idx}":
                            target_col = curr
                            break
                        curr = curr.right

                    if target_col and target_col.size > 0:
                        row_match = None
                        node = target_col.down
                        while node != target_col:
                            if node.info == (r, c, val):
                                row_match = node
                                break
                            node = node.down
                        if row_match:
                            self._cover(row_match.col)
                            j = row_match.right
                            while j != row_match:
                                self._cover(j.col)
                                j = j.right
                        else:
                            return 0

        solutions_count = 0

        def search():
            nonlocal solutions_count
            if solutions_count >= max_count:
                return
            if time.perf_counter() - start_ts > self.timeout_seconds:
                return

            if root.right == root:
                solutions_count += 1
                return

            min_col = None
            min_size = 999999
            c = root.right
            while c != root:
                if c.size < min_size:
                    min_size = c.size
                    min_col = c
                c = c.right

            if min_col is None or min_size == 0:
                return

            self._cover(min_col)

            r_node = min_col.down
            while r_node != min_col:
                j = r_node.right
                while j != r_node:
                    self._cover(j.col)
                    j = j.right

                search()

                j = r_node.left
                while j != r_node:
                    self._uncover(j.col)
                    j = j.left

                if solutions_count >= max_count:
                    self._uncover(min_col)
                    return

                r_node = r_node.down

            self._uncover(min_col)

        search()
        return solutions_count
