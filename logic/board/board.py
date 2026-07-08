class Board:


    def __init__(self,grid):

        self.grid = grid

        self.rows=len(grid)

        self.cols=len(grid[0])



    def is_inside(self,r,c):

        return (
            0 <= r < self.rows and
            0 <= c < self.cols
        )



    def get_piece(self,r,c):

        if self.is_inside(r,c):
            return self.grid[r][c]

        return None



    def move(self,start,end):

        sr,sc=start
        er,ec=end

        self.grid[er][ec]=self.grid[sr][sc]

        self.grid[sr][sc]="."



    def display(self):

        for row in self.grid:

            print(" ".join(row))
