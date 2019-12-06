import json
from random import randint

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import numpy as np
from scipy.signal import convolve2d

# Create your models here.

class AutoCreatedMixin(models.Model):
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        null=True, blank=True,
        unique=False, db_index=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id or not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.username


class Match(AutoCreatedMixin, models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='matches',
    )
    last_action_at = models.DateTimeField(
        verbose_name=_('Last action at'),
        null=True, blank=True,
        unique=False, db_index=True,
    )

    @classmethod
    def create(cls, user, rows, cols, mines):
        with transaction.atomic():
            match = Match.objects.create(user=user)  # pylint: disable=no-member

            Board.create(match, rows, cols, mines)
      
        return match

    def reveal(self, x, y):
        return self.board.reveal(x, y)


class Board(models.Model):
    CELL_MINE = -1

    CELL_VIS_REVEALED = 0
    CELL_VIS_HIDDEN = 1
    CELL_VIS_FLAGGED = 2

    USER_CELL_VIS_HIDDEN = -2
    USER_CELL_VIS_FLAGGED = -3


    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name='board',
    )

    rows = models.PositiveIntegerField()

    cols = models.PositiveIntegerField()

    cells = models.TextField()

    cells_visibility = models.TextField()

    @classmethod
    def create(cls, match, rows, cols, mines):
        cells = cls.generate_cells(rows, cols, mines)

        cells_ser = cls.serialize_cells(cells)  # serialize!

        cells_visibility = cls.generate_cells_visibility(rows, cols)

        cells_visibility_ser = cls.serialize_cells_visibility(cells_visibility)

        board = Board.objects.create(  # pylint: disable=no-member
            match=match,
            rows=rows,
            cols=cols,
            cells=cells_ser,
            cells_visibility=cells_visibility_ser,
        )
        return board

    @classmethod
    def generate_cells(cls, rows, cols, mines):
        mines_pos_list = []
        current_mines = 0

        # Start with a matrix of all zeros
        base_cells = np.zeros((rows, cols), dtype=int)

        # Generate a list of random mines positions
        while current_mines < mines:
            mine_pos_x = randint(0, rows - 1)
            mine_pos_y = randint(0, cols - 1)
            mine_pos = mine_pos_x, mine_pos_y

            if mine_pos not in mines_pos_list:
                mines_pos_list.append(mine_pos)
                current_mines += 1
        
        # Set mines with value of 1, so we can count them with convolution
        for mine_pos_x, mine_pos_y in mines_pos_list:
            base_cells[mine_pos_x][mine_pos_y] = 1
        
        # This filter sums neighbors
        sum_neighbors_filter = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ])

        # Now we have the mine count cells correct,
        # but mines representation cannot remain as 1
        cells = convolve2d(base_cells, sum_neighbors_filter, 'same')
        
        # Last stage is to set the mines with a value different
        # than a mine count (not a number >= 0)
        # Board.CELL_MINE is -1
        for mine_pos_x, mine_pos_y in mines_pos_list:
            cells[mine_pos_x][mine_pos_y] = Board.CELL_MINE

        return cells

    def get_cells_representation_for_user(self):
        cells_array = self.deserialize_cells(self.cells)
        cells_vis_array = self.deserialize_cells_visibility(self.cells_visibility)

        # 'hidden' (1) will get replaced by USER_CELL_VIS_HIDDEN (-2) for user representation
        cells_array[cells_vis_array == Board.CELL_VIS_HIDDEN] = Board.USER_CELL_VIS_HIDDEN
        # 'flagged' (2) will get replaced by USER_CELL_VIS_FLAGGED (-3) for user representation
        cells_array[cells_vis_array == Board.CELL_VIS_FLAGGED] = Board.USER_CELL_VIS_FLAGGED

        return self.serialize_cells(cells_array)

    def reveal(self, x, y):
        """
        Returns:
            -game_status:
                0 -> continue
                1 -> game over, mine found (lose)
                2 -> game over, finished (win)
            -revealed_cells:
                [{(pos_x, pos_y): cell_value}]
        """
        cells_array = self.deserialize_cells(self.cells)
        cells_vis_array = self.deserialize_cells_visibility(
            self.cells_visibility
        )

        cell = cells_array[x][y]
        if cell == Board.CELL_MINE:
            # Found mine
            return 1, {}
        elif cell > 0:
            # Found mine count number, cannot expand
            cells_revealed = {
                (x, y): cell,
            }
            cells_vis_array[x][y] = Board.CELL_VIS_REVEALED

            game_status = 0
        elif cell == 0:
            # Found empty mine count number, expand
            reveal_pos_list = self.expand_reveal(x, y, cells_array, cells_vis_array)

            cells_revealed = {
                (x, y): cell,
                **{(a, b): cells_array[a][b] for a, b in reveal_pos_list},
            }
            cells_vis_array[x][y] = Board.CELL_VIS_REVEALED

            game_status = 0
        else:
            raise Exception("Invalid case. Cell value: {}".format(cell))

        return game_status, cells_revealed

    def expand_reveal(self, x, y, cells_array, cells_vis_array):
        reveal_list = [(x, y)]
        propagate_list = [(x, y)]

        while propagate_list:
            current_propagate_list = propagate_list[:]
            propagate_list = []

            for cell_pos_x, cell_pos_y in current_propagate_list:
                nb_pos_list = self.get_neighbors_pos(
                    cell_pos_x, cell_pos_y, self.rows, self.cols,
                )

                for nb_pos_x, nb_pos_y in nb_pos_list:
                    nb_cell = cells_array[nb_pos_x][nb_pos_y]
                    nb_vis = cells_vis_array[nb_pos_x][nb_pos_y]
        
                    if nb_cell != Board.CELL_MINE and nb_vis != Board.CELL_VIS_REVEALED:
                        # Update for user target return
                        reveal_list.append((nb_pos_x, nb_pos_y))
                        # Update for model
                        cells_vis_array[nb_pos_x][nb_pos_y] = Board.CELL_VIS_REVEALED

                        if nb_cell == 0:
                            propagate_list.append((nb_pos_x, nb_pos_y))

        return reveal_list

    @classmethod
    def get_neighbors_pos(self, x, y, x_limit, y_limit):
        # Maybe can be optimized by using only neighbors
        # from up, down, left, right
        pos_list = []

        # (x - 1, *)
        if x > 0:
            if y > 0:
                pos = (x - 1, y - 1)
                pos_list.append(pos)

            pos = (x - 1, y)
            pos_list.append(pos)

            if y < y_limit - 1:
                pos = (x - 1, y + 1)
                pos_list.append(pos)
        
        # (x, * != y)
        if y > 0:
            pos = (x, y - 1)
            pos_list.append(pos)

        if y < y_limit - 1:
            pos = (x, y + 1)
            pos_list.append(pos)

        # (x + 1, *)
        if x < x_limit - 1:
            if y > 0:
                pos = (x + 1, y - 1)
                pos_list.append(pos)

            pos = (x + 1, y)
            pos_list.append(pos)

            if y < y_limit - 1:
                pos = (x + 1, y + 1)
                pos_list.append(pos)
        
        return pos_list

    @classmethod
    def serialize_cells(cls, cells_array):
        cells_str = json.dumps(cells_array.tolist())
        
        # Remove empty space
        cells_str.replace(' ', '')

        return cells_str

    @classmethod
    def deserialize_cells(cls, cells_str):
        cells_data = json.loads(cells_str)
        cells_array = np.asarray(cells_data)
        return cells_array

    @classmethod
    def generate_cells_visibility(cls, rows, cols):
        # Initialize with 1's as that marks hidden
        cells_vis = np.ones((rows, cols))
        return cells_vis

    @classmethod
    def serialize_cells_visibility(cls, cells_vis_array):
        cells_vis_str = json.dumps(cells_vis_array.tolist())
        
        # Remove empty space
        cells_vis_str.replace(' ', '')

        return cells_vis_str

    @classmethod
    def deserialize_cells_visibility(cls, cells_vis_str):
        cells_vis_data = json.loads(cells_vis_str)
        cells_vis_array = np.asarray(cells_vis_data)
        return cells_vis_array