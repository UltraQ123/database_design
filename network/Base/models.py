import peewee as pw

from . import database
from flask_login import UserMixin
from werkzeug.security import check_password_hash
class BaseModel(pw.Model):
    class Meta:
        database = database


class Cards(BaseModel):
    id = pw.IntegerField(null=False, primary_key=True)
    name = pw.CharField(max_length=255,null=False)
    card_type = pw.CharField(column_name="type", max_length=255,constraints=[pw.Check("type in (\"怪兽\", \"魔法\", \"陷阱\"")])
    is_ocg = pw.BooleanField(column_name='isOcg', default=True)
    is_tcg = pw.BooleanField(column_name='isTcg', default=True)

    class Meta:
        table_name = 'cards'


class Cardbag(BaseModel):
    id = pw.IntegerField(primary_key=True)
    time = pw.DateField(column_name='Time', null=True)
    name = pw.CharField(max_length=1024)
    short_name = pw.CharField(column_name="short_name",max_length=255)

    class Meta:
        table_name = 'cardbag'


class Bagcontent(BaseModel):
    card_bag = pw.ForeignKeyField(column_name='CardBagId', field='id', model=Cardbag)
    cardid = pw.ForeignKeyField(column_name='Cardid', field='id', model=Cards)
    class Meta:
        table_name = 'bagcontent'
        indexes = (
            (('card_bag', 'cardid'), True),
        )
        primary_key = pw.CompositeKey('card_bag', 'cardid')


class User(BaseModel,UserMixin):
    name = pw.CharField(primary_key=True,max_length=255)
    password = pw.CharField(max_length=255)
    email = pw.CharField(max_length=255)
    isAdmin = pw.BooleanField(default=False)
    class Meta:
        table_name = 'user'

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Cardset(BaseModel):
    last_alter_time = pw.DateField(column_name='LastAlterTime', null=True)
    create_time = pw.DateField(column_name='createTime', null=True)
    name = pw.CharField(max_length=255)
    user = pw.ForeignKeyField(column_name='user', field='name', model=User)

    class Meta:
        table_name = 'cardset'
        indexes = (
            (('user', 'name'), True),
        )
        primary_key = pw.CompositeKey('name', 'user')


class Forbiddencard(BaseModel):
    cardid = pw.ForeignKeyField(column_name='Cardid', field='id', model=Cards)
    env = pw.CharField(column_name='env',null=False)
    number = pw.IntegerField(column_name='Number',constraints=[pw.Check("Number>=0 and Number<3")])
    time = pw.DateField()

    class Meta:
        table_name = 'forbiddencard'
        indexes = (
            (('cardid', 'time',"env"), True),
        )
        primary_key = pw.CompositeKey('cardid', 'time',"env")

class Magiccards(BaseModel):
    cardid = pw.ForeignKeyField(column_name='Cardid', field='id', model=Cards, primary_key=True)
    effect = pw.CharField(max_length=1024)
    type = pw.CharField(constraints=[pw.Check("type in (\"通常\",\"永续\",\"速攻\",\"仪式\",\"装备\",\"场地\"")])

    class Meta:
        table_name = 'magiccards'

class Monstercards(BaseModel):
    cardid = pw.ForeignKeyField(column_name='Cardid', field='id', model=Cards, primary_key=True)
    type = pw.CharField(max_length=255)
    pendulum_number = pw.IntegerField(column_name='PendulumNumber', null=True)
    _atk = pw.IntegerField(column_name='atk')
    _def = pw.IntegerField(column_name='def', null=True)
    is_effect = pw.BooleanField(column_name="isEffect",default=False)
    is_cartoon = pw.BooleanField(column_name="isCartoon",default=False)
    is_special = pw.BooleanField(column_name="isSpecial",default=False)
    is_alliance = pw.BooleanField(column_name='isAlliance', default=False)
    is_double = pw.BooleanField(column_name='isDouble', default=False)
    is_normal = pw.BooleanField(column_name='isNormal', default=False)
    is_reversal = pw.BooleanField(column_name='isReversal', default=False)
    is_soul = pw.BooleanField(column_name='isSoul', default=False)
    is_token = pw.BooleanField(column_name='isToken', default=False)
    is_tuner = pw.BooleanField(column_name='isTuner', default=False)
    link_mark = pw.IntegerField(column_name='linkMark', null=True,constraints=[pw.Check("linkMark > 0")])
    monster_effect = pw.CharField(column_name='monsterEffect', null=True,max_length=1024)
    pendulum_effect = pw.CharField(column_name='pendulumEffect', null=True,max_length=1024)
    star_number = pw.IntegerField(column_name='starNumber')
    race = pw.CharField(column_name="race",max_length=255,null=False)
    attrib = pw.CharField(column_name="attrib",max_length=255,null=False)
    class Meta:
        table_name = 'monstercards'



class Setcontent(BaseModel):
    cardid = pw.ForeignKeyField(column_name='Cardid', field='id', model=Cards)
    set_name = pw.ForeignKeyField(backref='cardset_set_user_set', column_name='SetName', field='name', model=Cardset)
    set_user = pw.ForeignKeyField(backref='cardset_set_user_set', column_name='SetUser', field='user', model=Cardset)
    number = pw.IntegerField(null=False,constraints=[pw.Check("number>0")])
    position = pw.IntegerField(null=False,column_name="position",constraints=[pw.Check("position>=0 and position<=2")])
    class Meta:
        table_name = 'setcontent'
        indexes = (
            (('set_user', 'set_name', 'cardid',"position"), True),
        )
        primary_key = pw.CompositeKey('set_name', 'set_user','cardid',"position")

class Trapcards(BaseModel):
    cardid = pw.ForeignKeyField(column_name='Cardid', field='id', model=Cards, primary_key=True)
    effect = pw.CharField()
    type = pw.CharField(constraints=[pw.Check("type in ((\"通常\",\"永续\",\"反击\"")])

    class Meta:
        table_name = 'trapcards'

