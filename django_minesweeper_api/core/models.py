from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

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


class Board(models.Model):
    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name='board',
    )

    rows = models.PositiveIntegerField()

    cols = models.PositiveIntegerField()

    cells = models.TextField()

    @classmethod
    def create(cls, match, rows, cols, mines):
        cells = cls.generate_cells(rows, cols, mines)

        cells = str(cells)  # serialize!

        board = Board.objects.create(  # pylint: disable=no-member
            match=match,
            rows=rows,
            cols=cols,
            cells=cells,
        )
        return board

    @classmethod
    def generate_cells(cls, rows, cols, mines):
        return []
