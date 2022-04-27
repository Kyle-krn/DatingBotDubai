from decimal import Decimal
from tortoise import Model, fields



class UserModel(Model):
    id: int = fields.IntField(pk=True)
    tg_id: int = fields.BigIntField()
    tg_username: str = fields.CharField(max_length=255, null=True)
    # profile: fields.OneToOneRelation["Profile"]
    

# class Profile(Model):
#     id: int = fields.IntField(pk=True)
    # user: fields.OneToOneRelation = fields.OneToOneField("models.UserModel", related_name="profile")
    male: bool = fields.BooleanField(null=True)
    name: str = fields.CharField(max_length=255, null=True)
    about_me: str = fields.TextField(null=True)
    lat: Decimal = fields.DecimalField(max_digits=10, decimal_places=6, null=True)
    long: Decimal = fields.DecimalField(max_digits=10, decimal_places=6, null=True)
    address: str = fields.TextField(null=True)
    moving_to_dubai: bool = fields.BooleanField(null=True)
    birthday = fields.DateField(null=True)
    # interest_place_companion = fields.ForeignKeyField('models.DatingInterestPlace', related_name='profiles')
    interest_place_companion = fields.CharField(max_length=255, null=True)
    
    hobbies: fields.ManyToManyRelation["Hobbies"] = fields.ManyToManyField(
        "models.Hobbies", related_name="users", through="users_hobbies"
    )

    children_age: list = fields.JSONField(default=[]) 
    photo_path: str = fields.TextField(null=True)
    # children: fields.ManyToManyRelation["Hobbies"] = fields.ManyToManyField(
    #     "models.Hobbies", related_name="profiles", through="users_hobbies"
    # )



# class DatingInterestPlace(Model):
#     id: int = fields.IntField(pk=True)
#     title_interest: str = fields.CharField()
# class ChildrenAge(Model):
#     id: int = fields.IntField(pk=True)
#     children_age: int = fields.IntField()
class PurposeOfDating(Model):
    id: int = fields.IntField(pk=True)
    title_purp: str = fields.CharField(max_length=255)

class Hobbies(Model):
    id: int = fields.IntField(pk=True)
    title_hobbie: str = fields.CharField(max_length=255)
    # profiles: fields.ManyToManyRelation["Profile"]
