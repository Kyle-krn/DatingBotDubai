from decimal import Decimal
from datetime import datetime
from email.policy import default
from tortoise import Model, fields


class UserModel(Model):
    id: int = fields.IntField(pk=True)
    tg_id: int = fields.BigIntField()
    tg_username: str = fields.CharField(max_length=255, null=True)
    male: bool = fields.BooleanField(null=True)
    name: str = fields.CharField(max_length=255, null=True)
    # about_me: str = fields.TextField(null=True)
    lat: Decimal = fields.DecimalField(max_digits=10, decimal_places=6, null=True)
    long: Decimal = fields.DecimalField(max_digits=10, decimal_places=6, null=True)
    place: str = fields.TextField(null=True)
    dubai: bool = fields.BooleanField(default=False)
    moving_to_dubai: bool = fields.BooleanField(null=True)
    birthday = fields.DateField(null=True)
    interest_place_companion: fields.ManyToManyRelation["DatingInterestPlace"] = fields.ManyToManyField(
        "models.DatingInterestPlace", related_name="users", through="interest_place_user"
    )
    hobbies: fields.ManyToManyRelation["Hobbies"] = fields.ManyToManyField(
        "models.Hobbies", related_name="users", through="users_hobbies"
    )
    tmz: int = fields.IntField(null=True)
    children: bool = fields.BooleanField(null=True)
    children_age: list = fields.JSONField(default=[]) 
    marital_status: str = fields.CharField(max_length=255, null=True)

    purp_dating: fields.ManyToManyRelation["PurposeOfDating"] = fields.ManyToManyField(
        "models.PurposeOfDating", related_name="users", through="users_purp"
    )
    end_premium: datetime = fields.DatetimeField(null=True)
    avatar: fields.OneToOneRelation["AvatarModel"]
    superlike_count: int = fields.IntField(default=1)

    verification: bool = fields.BooleanField(default=False)
    ban: bool = fields.BooleanField(default=False)
    end_registration: bool = fields.BooleanField(default=False) 

    free_likes = fields.IntField(default=3)

    user_view: fields.ReverseRelation["UserView"]
    search_settings: fields.ReverseRelation["UserSearchSettings"]

    # class Meta:
    #     table = 'user'

    def __str__(self):
        return f"User #{self.id}: {self.tg_username}"


class UserSuccesPayments(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="payments"
    )
    createad_at: datetime = fields.DatetimeField(auto_now_add=True)
    amount: Decimal = fields.DecimalField(max_digits=10, decimal_places=2)
    product: str = fields.CharField(max_length=200) # Gold | Superlike
    count_mount_prem: int = fields.IntField(null=True) 
    superlike_count: int = fields.IntField(null=True)

class UsersRelations(Model):
    '''Процент совместимости междую юзерами'''
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="user_relation"
    )
    target_user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="target_user_relation"
    )
    percent_compatibility: int = fields.IntField()
    
    result_distance_check: bool = fields.BooleanField()
    result_purp_check: bool = fields.BooleanField()

    percent_age: int = fields.IntField()
    percent_children: int = fields.IntField()
    percent_hobbies: int = fields.IntField()

    result_gender_check: bool = fields.BooleanField()

    # class Meta:
    #     table = 'users_relations'


class UserSearchSettings(Model):
    id: int = fields.IntField(pk=True)
    user: fields.OneToOneRelation[UserModel] = fields.OneToOneField("models.UserModel", related_name="search_settings")
    male: bool = fields.BooleanField(null=True)
    min_age: int = fields.IntField(null=True)
    max_age: int = fields.IntField(null=True)
    children: bool = fields.BooleanField(null=True)
    children_min_age: int = fields.IntField(null=True)
    children_max_age: int = fields.IntField(null=True)

    # class Meta:
    #     table = "user_settings"

class UserView(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="user_view")
    target_user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="target_user_view")
    relation: fields.ForeignKeyRelation["UsersRelations"] = fields.ForeignKeyField(
        "models.UsersRelations", related_name="relation_view")
    count_view: int = fields.IntField(default=0)

    like: bool = fields.BooleanField(default=False)
    superlike: bool = fields.BooleanField(default=False)
    dislike: bool = fields.BooleanField(default=False)
    
    # class Meta:
    #     table = 'user_view'


class MutualLike(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="mutal_like")
    target_user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="target_mutal_like")
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    # class Meta:
    #     table = "mutal_like"



class AvatarModel(Model):
    '''Аватар'''
    id: int = fields.IntField(pk=True)
    file_id: str = fields.CharField(max_length=255)
    file_path: str = fields.CharField(max_length=255)
    file_type: str = fields.CharField(max_length=40)
    photo_bool: bool = fields.BooleanField()
    user: fields.OneToOneRelation[UserModel] = fields.OneToOneField("models.UserModel", related_name="avatar")
    # class Meta:
    #     table = "user_avatar"


class DatingInterestPlace(Model):
    id: int = fields.IntField(pk=True)
    title_interest: str = fields.CharField(max_length=255)

    def __str__(self):
        return self.title_interest

    # class Meta:
    #     table = "dating_interest_place"


class PurposeOfDating(Model):
    id: int = fields.IntField(pk=True)
    title_purp: str = fields.CharField(max_length=255)
    users: fields.ManyToManyRelation["UserModel"]

    # class Meta:
    #     table = "dating_purpose"


class Hobbies(Model):
    id: int = fields.IntField(pk=True)
    title_hobbie: str = fields.CharField(max_length=255, unique=True)
    users: fields.ManyToManyRelation["UserModel"]

    # class Meta:
    #     table = "hobbie"


