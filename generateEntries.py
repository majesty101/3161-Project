import pandas as pd
from faker import Faker
from collections import defaultdict
from sqlalchemy import create_engine,MetaData,Column,String,Integer,Table
from sqlalchemy_utils import database_exists, create_database
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
        fake_data['allergies'].append(fake.word(allergy_list))
        fake_data['account_number'].append("AC-" + str(i))

    df_fake_data = pd.DataFrame(fake_data)
    df_fake_data.to_sql('accounts',con=engine.connect(),index=False,if_exists='append')

def fakeRecipe():
    fake_data = defaultdict(list)
    for i in range(1000):
        fake_data["recID"].append("RE-" + str(i))
        fake_data["title"].append(fake.word())
        fake_data["calories"].append(fake.random_int(min=100,max=600))
        fake_data["descripton"].append(fake.sentence())
        fake_data["dateAdded"].append(fake.date())
 
    df_fake_data = pd.DataFrame(fake_data)
    df_fake_data.to_sql('recipe',con=engine.connect(),index=False,if_exists='append')
        
def createTables():

    
    accounts = Table(
        'accounts',meta,
        Column('first_name',String(50)),
        Column('last_name',String(50)),
        Column('password',String(10)),
        Column('allergies',String(20)),
        Column('account_number',String(10),primary_key=True),
    )
    recipe = Table(
        'recipe',meta,
        Column('recID',String(50),primary_key=True),
        Column('title',String(50)),
        Column('calories',String(10)),
        Column('descripton',String(50)),
        Column('dateAdded',String(10)),
    )
    meta.create_all(engine,checkfirst=True)

def createDB():
    create_database(engine.url)
     
    

if __name__ == '__main__':
    createDB()
    createTables()
    fakeAccount()
    fakeRecipe()
