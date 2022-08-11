import numpy as np
import random
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class MW_Grid:
    ''' minesweeper grid containing all fields'''

    def __init__(self,
                 size: tuple = (16, 16), num_of_bombs: int = 40) -> None:
        self.size = size
        self.num_of_bombs = num_of_bombs
        self.fields = self.initialize_grid()
        self.ax = self.plot_init()
        self.first_move()

        self.game_over = False
        self.main_loop()
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
        plt.tight_layout()
        return ax
        
        '''
        while True:
            coords = plt.ginput(1)[0]
            coords = tuple([round(c) for c in coords])
            self.fields[coords].reveal()
        '''

    def first_move(self) -> None:
        ''' distribute bombs after first click'''
        first_pick = plt.ginput(1)[0]
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
    
    def main_loop(self) -> None:
        while not self.game_over:
            picked_tile = plt.ginput(1, timeout=0)[0]
            picked_tile = tuple([round(c) for c in picked_tile])
            self.fields[picked_tile].reveal()



    
    def reveal_all_fields(self):
        ''' reveal all tiles from the fields'''
        for field in self.fields.values():
            field.remove_tile()


        

        


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
        '*' : 'k',
        'X' : 'k',
        u'\u2738': 'k'
    }
    
    def __init__(self, grid: MW_Grid, position: tuple, is_bomb: bool) -> None:
        self.grid = grid
        self.position = position
        self.is_bomb = is_bomb
        self.revealed = False
    
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
        self.tile = patches.Rectangle((self.position[0]-0.5, self.position[1]-0.5), 1, 1, fc='grey', zorder=10)
        ax.add_patch(self.tile)
    
    def reveal(self) -> None:
        ''' reveal if field is bomb and remove tile'''
        if not self.revealed:
            self.revealed = True
            self.tile.remove()
            plt.draw()

            if self.is_bomb:
                print(f'Bomb on field {self.position} exploded!')
                self.grid.reveal_all_fields()
                self.grid.game_over = True
            elif self.surrounding_bombs == 0:
                # recursively reveal all other tiles
                print(f'try to remove tile {self.position}')
                for nn in self.get_nearest_neighbors():
                    if not self.grid.fields[nn].revealed:
                        self.grid.fields[nn].reveal()
            else:
                print(f'clicked on field {self.position}: no bomb')

    
    def remove_tile(self) -> None:
        ''' just remove the tile'''
        if not self.revealed:
            self.revealed = True
            self.tile.remove()
            plt.draw()
        


if __name__ == '__main__':
    test = MW_Grid()

    

        

