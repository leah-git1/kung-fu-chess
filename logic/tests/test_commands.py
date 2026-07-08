from commands.click_command import ClickCommand
from commands.wait_command import WaitCommand
from commands.print_command import PrintBoardCommand


class DummyGame:


    def __init__(self):

        self.clicked=None
        self.waited=None
        self.printed=False



    def handle_click(self,r,c):

        self.clicked=(r,c)



    def advance_time(self,time):

        self.waited=time



    def update_moves(self):

        pass



    class Board:

        def display(self):
            pass


    board=Board()



def test_click_command():

    game=DummyGame()

    cmd=ClickCommand(150,50)

    cmd.execute(game)


    assert game.clicked==(0,1)



def test_wait_command():

    game=DummyGame()

    cmd=WaitCommand(500)

    cmd.execute(game)


    assert game.waited==500



def test_print_command():

    game=DummyGame()

    cmd=PrintBoardCommand()

    cmd.execute(game)