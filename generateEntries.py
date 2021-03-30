import pandas as pd
from faker import Faker
from collections import defaultdict
from sqlalchemy import create_engine,MetaData,Column,String,Integer,Table
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils.functions.database import drop_database
meta = MetaData()
fake=Faker()
engine = create_engine('mysql://root:@localhost/recipeDB') 
allergy_list = ['Milk','Eggs','Nuts','Shellfish','Soy','Wheat','None']


def fakeAccount():
    fake_data = defaultdict(list)
    for i in range(1000):
        fake_data["first_name"].append(fake.first_name())
        fake_data["last_name"].append(fake.last_name())
        fake_data['password'].append(fake.password(length=12))
        fake_data['AccID'].append("AC-" + str(i))

    df_fake_data = pd.DataFrame(fake_data)
    df_fake_data.to_sql('accounts',con=engine.connect(),index=False,if_exists='append')

def fakeRecipe():
    fake_data = defaultdict(list)
    for i in range(1000):
        fake_data["RecID"].append("RE-" + str(i))
        fake_data["title"].append(fake.word())
        fake_data["calories"].append(fake.random_int(min=100,max=600))
        fake_data["descripton"].append(fake.sentence())
        fake_data["dateAdded"].append(fake.date())
        # add prep time 
 
    df_fake_data = pd.DataFrame(fake_data)
    df_fake_data.to_sql('recipe',con=engine.connect(),index=False,if_exists='append')
        
def createTables():

    
    accounts = Table(
        'accounts',meta,
        Column('first_name',String(50)),
        Column('last_name',String(50)),
        Column('password',String(10)),
        Column('AccID',String(10),primary_key=True)
    )

    allergies = Table(
        'allergies',meta,
        Column('AccID',String(10),ForeignKey('accounts.AccID',ondelete='CASCADE'),primary_key=True ),
        Column('allergy',String(20))
    )
    recipe = Table(
        'recipes',meta,
        Column('RecID',String(50),primary_key=True),
        Column('title',String(50)),
        Column('calories',String(10)),
        Column('descripton',String(50)),
        Column('dateAdded',String(10)),
        Column('prepTime',String(10)),
    )

    category = Table(
        'category',meta,
        Column('RecID',String(10),ForeignKey('recipes.RecID',ondelete='CASCADE'),primary_key=True ),
        Column('category',String(20))
    )

    meal = Table(
        'meals',meta,
        Column('mealID',String(10),primary_key=True),
        Column('mealNa',String(20)),
        Column('mealImg',String(225))
    )

    recIn = Table(
        'instrut',meta,
        Column('RecID',String(10),ForeignKey('recipes.RecID',ondelete='CASCADE'),primary_key=True ),
        Column('InstrID',String(10)),
        Column('IngreQua',String(10))
    )

    recDec = Table(
        'recDesc',meta,
        Column('RecID',String(10),ForeignKey('recipes.RecID',ondelete='CASCADE'),primary_key=True ),
        Column('Desc',String(255))
    )

    ingre = Table(
        'ingredients',meta,
        Column('ingredientID',String(10),primary_key=True),
        Column('name',String(30)),
        Column('qty',Integer),
        Column('unit',Integer)
    )
    meta.create_all(engine,checkfirst=True)

def createDB():
    if not database_exists(engine.url):
        create_database(engine.url)
    else:
        drop_database(engine.url)
        create_database(engine.url)
     
    

if __name__ == '__main__':
    createDB()
    createTables()

