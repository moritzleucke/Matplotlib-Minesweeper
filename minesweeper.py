#!/usr/bin/env python3
import numpy as np
import random
import time 
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class MW_Grid:
    ''' minesweeper grid containing all fields'''

    @classmethod
    def beginner(cls):
        return cls((9, 9), 10)
    
    @classmethod
    def intermediate(cls):
        return cls((16, 16), 40)
    
    @classmethod 
    def hard(cls):
        return cls((30, 16), 99)


    def __init__(self, size: tuple[int,int], num_of_bombs: int) -> None:
        self.size = size
        self.num_of_bombs = num_of_bombs
        self.fields = self.initialize_grid()
        self.fig, self.ax = self.plot_init()
        self.num_tiles_left = size[0]*size[1]
        self.first_move()

        self.game_over = False
        self.num_flags = self.num_of_bombs + 0
        cid = self.fig.canvas.mpl_connect('button_press_event', self.user_interaction)
        plt.show()

    def initialize_grid(self) -> dict:
        ''' initialize the grid fields'''
        fields = {}
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                fields[(i, j)] = Field(self, (i, j), is_bomb=False)
        return fields  
    
    def plot_init(self) -> plt.Axes:
        ''' display the whole field in matplotlib'''
        fig = plt.figure(figsize=(self.size[0]*0.3, self.size[1]*0.3))
        ax = fig.add_subplot(111)

        for field in self.fields.values():
            field.plot_tile(ax)
        
        # grid lines
        for x in np.arange(-0.5, self.size[0]-0.5):
            plt.axvline(
                x,
                ymin=-0.5,
                ymax = self.size[1] + 0.5,
                color = 'k',
                zorder = 20
            )
        for y in np.arange(-0.5, self.size[1]-0.5):
            plt.axhline(
                y,
                xmin=-0.5,
                xmax=self.size[0] + 0.5,
                color = 'k',
                zorder = 20
            )
            
        ax.set_xlim((-0.5, self.size[0]-0.5))
        ax.set_xlabel('')
        ax.set_xticks([])
        ax.set_ylim((-0.5, self.size[1]-0.5))
        ax.set_ylabel('')
        ax.set_yticks([])
        ax.set_facecolor('gainsboro')
        ax.set_title(
            f'remaining flags: {self.num_of_bombs}/{self.num_of_bombs}', 
            loc='left', 
            fontweight='bold', 
            fontsize=14, 
            pad=10
        )
        plt.tight_layout()
        return fig, ax

    def first_move(self) -> None:
        ''' distribute bombs after first click'''
        first_pick = plt.ginput(1)[0]
        self.start_time = time.time()
        first_pick = tuple([round(c) for c in first_pick])
         # nearest neighbours of first pick
        no_bombs_idx = self.fields[first_pick].get_nearest_neighbors()
        no_bombs_idx.append(first_pick)

        # distribute the bombs
        possible_bomb_idx = []
        for idx in self.fields.keys():
            if idx not in no_bombs_idx:
                possible_bomb_idx.append(idx)
        random.shuffle(possible_bomb_idx)
        for i in range(self.num_of_bombs):
            self.fields[possible_bomb_idx[i]].is_bomb = True
        
        # count surrounding bombs
        for field in self.fields.values():
            field.count_surrounding_bombs()
            field.plot_number(self.ax)
        
        # reveal first tiles
        for idx in no_bombs_idx:
            print('tile removed')
            self.fields[idx].reveal()
        self.fig.canvas.draw()
    
    def reveal_all_fields(self):
        ''' reveal all tiles from the fields'''
        for field in self.fields.values():
            if not field.flagged:
                field.remove_tile()
        self.fig.canvas.draw()


    def user_interaction(self, event) -> None:
        ''' reveal or flag a field'''
        idx = (round(event.xdata), round(event.ydata))
        if event.button == 1:
            self.fields[idx].reveal()
        elif event.button == 3:
            self.fields[idx].flag_tile(self.ax)
        self.fig.canvas.draw()
    
    def update_title(self) -> None:
        ''' update the title with status information'''
        self.ax.set_title(
            f'remaining flags: {self.num_flags}/{self.num_of_bombs}', 
            loc='left', 
            fontweight='bold', 
            fontsize=14,
            pad=10
        )
    
    def count_unopened_tiles(self) -> int:
        ''' count the tiles that aren't removed yet'''
        tiles_left = 0
        for field in self.fields:
            if not field.revealed: 
                tiles_left +=1
        return tiles_left
    
    def plot_win_screen(self) -> None:
        ''' display if user wins'''
        game_time = time.time() - self.start_time
        self.ax.set_title(
            f'You won!', 
            loc='left', 
            fontweight='bold', 
            color = 'green',
            fontsize=14,
            pad=10
        )
        self.ax.set_title(
            f'{game_time:.0f} s',
            loc='right',
            fontweight='bold', 
            color = 'green',
            fontsize=14,
            pad=10
        )
    
    def plot_game_over_screen(self) -> None:
        ''' display if user lost the game'''
        self.ax.set_title(
            f'Game over!', 
            loc='left', 
            fontweight='bold', 
            color = 'red',
            fontsize=14,
            pad=10
        )
        

        


class Field:
    ''' one field of the minesweeper grid'''

    number_color = {
        0 : 'gainsboro',
        1 : 'tab:blue',
        2 : 'tab:green',
        3 : 'tab:red',
        4 : 'magenta',
        5 : 'tab:orange',
        6 : 'turquoise',
        7 : 'grey',
        8 : 'black',
        u'\u2738': 'k'
    }
    
    def __init__(self, grid: MW_Grid, position: tuple, is_bomb: bool) -> None:
        self.grid = grid
        self.position = position
        self.is_bomb = is_bomb
        self.revealed = False
        self.flagged = False
    
    def count_surrounding_bombs(self) -> None:
        ''' count the bombs in the nearest neighborhood'''
        nn_list = self.get_nearest_neighbors()
        surrounding_bombs = 0
        for nn in nn_list:
            if self.grid.fields[nn].is_bomb:
                surrounding_bombs +=1
        self.surrounding_bombs = surrounding_bombs


    def get_nearest_neighbors(self) -> list[tuple]:
        ''' calculate the position of the nearest neighbors'''
        self_idx = np.array(self.position)
        shifts = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1)
        ]
        nn_list = [tuple(self_idx + shift) for shift in shifts]
        valid_nns = []
        for nn in nn_list:
            if nn in self.grid.fields.keys():
                valid_nns.append(nn)
        return valid_nns
    
    def plot_number(self, ax: plt.Axes) -> None:
        ''' plot the number of surrounding bombs'''
        if self.is_bomb:
            char = u'\u2738'
            # flag: u'\u2691' 
        else:
            char = self.surrounding_bombs
        ax.text(
            x = self.position[0],
            y = self.position[1],
            s = str(char),
            fontsize = 14,
            ha = 'center',
            va = 'center',
            color = self.number_color[char],
            fontweight = 'bold'
        )

    def plot_tile(self, ax: plt.Axes) -> None:
        ''' plot field to matplotlib axes'''
        self.tile = patches.Rectangle(
            (self.position[0]-0.5, self.position[1]-0.5), 1, 1, 
            fc='grey', 
            zorder=10
        )
        ax.add_patch(self.tile)
    
    def flag_tile(self, ax: plt.Axes) -> None:
        ''' flag or unflag tile'''
        if not self.flagged and not self.revealed:
            self.flagged = True
            self.flag = ax.text(
                self.position[0],
                self.position[1],
                u'\u2691',
                fontsize = 14,
                va = 'center',
                ha = 'center',
                color = 'white',
                zorder = 30
            )
            print(f'flagged field {self.position}')
            self.grid.num_flags -=1
        elif self.flagged:
            self.flagged = False
            self.flag.remove()
            print(f'removed flag on field {self.position}')
            self.grid.num_flags +=1
        self.grid.update_title()
    
    def reveal(self, recursive=True) -> None:
        ''' reveal if field is bomb and remove tile'''
        if not self.revealed and not self.flagged:
            self.revealed = True
            self.tile.remove()
            self.grid.num_tiles_left -=1

            if self.is_bomb:
                print(f'Bomb on field {self.position} exploded!')
                self.grid.reveal_all_fields()
                self.grid.game_over = True
                self.grid.plot_game_over_screen()
            elif self.surrounding_bombs == 0:
                # recursively reveal all other tiles
                for nn in self.get_nearest_neighbors():
                    if not self.grid.fields[nn].revealed:
                        self.grid.fields[nn].reveal()
            elif self.grid.num_tiles_left == self.grid.num_of_bombs:
                # game ended: winning
                self.grid.game_over = True
                self.grid.plot_win_screen()
            else:
                print(f'clicked on field {self.position}: no bomb')

        elif self.revealed and recursive:
            # reveal sourrounding fields
            if self.check_matching_sourrounding_flags():
                for nn in self.get_nearest_neighbors():
                    self.grid.fields[nn].reveal(recursive=False)

    
    def check_matching_sourrounding_flags(self) -> bool:
        ''' check if souurrounding flags is matching the num of sourr. bombs'''
        flags = 0
        for nn in self.get_nearest_neighbors():
            if self.grid.fields[nn].flagged:
                flags +=1
        return (flags == self.surrounding_bombs)
            

    
    def remove_tile(self) -> None:
        ''' just remove the tile'''
        if not self.revealed:
            self.revealed = True
            self.tile.remove()
            
        


if __name__ == '__main__':
    #test = MW_Grid.intermediate()
    MW_Grid((16, 16), 10)

    

        

