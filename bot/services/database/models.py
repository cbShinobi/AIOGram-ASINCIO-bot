from tortoise import fields
from tortoise.models import Model


class BotUser(Model):
    id = fields.IntField(pk=True, unique=True)  # telegram user id
    username = fields.TextField(null=True)
    full_name = fields.TextField()

    @property
    def contacts(self):
        if self.username:
            return f"@{self.username} {self.full_name}"

        return self.full_name


class Game(Model):
    id = fields.IntField(pk=True, unique=True)
    name = fields.TextField()
    location = fields.TextField()
    description = fields.TextField()
    seats = fields.IntField()
    starts_at = fields.DatetimeField()
    created_by: fields.ForeignKeyRelation[BotUser] = fields.ForeignKeyField(
        "models.BotUser", related_name="games"
    )
    members: fields.ReverseRelation["GameMember"]


class GameMember(Model):
    id = fields.IntField(pk=True, unique=True)
    game: fields.ForeignKeyRelation[Game] = fields.ForeignKeyField(
        "models.Game", related_name="members"
    )
    bot_user: fields.ForeignKeyRelation[BotUser] = fields.ForeignKeyField(
        "models.BotUser", related_name="game_memberships"
    )
