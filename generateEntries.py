import pandas as pd
from faker import Faker
from collections import defaultdict
from sqlalchemy import create_engine,MetaData,Column,String,Integer,Table
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils.functions.database import drop_database
from sqlalchemy.types import Date
meta = MetaData()
fake=Faker()
engine = create_engine('mysql://root:@localhost/recipeDB') 
allergy_list = ['Dairy','Eggs','Nuts','Shellfish','Soy','Wheat','Gluten','None','Seafood']
category = ['Breakfast','Lunch','Dinner']




"""
Populate Tables
"""


NUM_ACC = 1000
NUM_RECIPE = 1000
def fakeAccount():
    fake_data = defaultdict(list)
    for i in range(1,NUM_ACC+1):
        fake_data["first_name"].append(fake.first_name())
        fake_data["last_name"].append(fake.last_name())
        fake_data['password'].append(fake.password(length=12))
        fake_data['AccID'].append("AC-" + str(i))

    commit(fake_data,'accounts')

def fakeRecipe():
    desc = defaultdict(list)
    fake_data = defaultdict(list)
    for i in range(1,NUM_RECIPE+1):
        fake_data["RecID"].append("RE-" + str(i))
        fake_data["title"].append(fake.word())
        fake_data["calories"].append(fake.random_int(min=100,max=1000))
        fake_data["DescID"].append('DESC-' + str(i))
        fake_data["dateAdded"].append(fake.date())
        fake_data['prepTime'].append(fake.pyint(5,75))
        desc['DescID'].append('DESC-' + str(i))
        desc['Desc'].append(fake.sentence())
    commit(desc,'recipe_description')
    commit(fake_data,'recipes')

def generateAllergies():
    fake_data = defaultdict(list)
    for i in range(1,len(allergy_list)+1):
        fake_data['name'].append(allergy_list[i-1])
        fake_data['AllID'].append("AL-" + str(i) )
    commit(fake_data,'allergies')



def generateUserAllergies():
    fake_data = defaultdict(list)
    for i in range(1,NUM_ACC+1):
        fake_data['AccID'].append("AC-" + str(i))#IN the future make a person have more than one allergy
        fake_data['AllID'].append("AL-" + str(fake.pyint(1,len(allergy_list))))

    commit(fake_data,'user_allergies')

def generateCategories():
    fake_data = defaultdict(list)
    for i in range(1,NUM_RECIPE+1):
        fake_data['RecID'].append("RE-" + str(i))
        fake_data['category'].append(fake.word(category))
    commit(fake_data,'categories')

def generateIng():
    fake_data = defaultdict(list)
    ing ='''salt
pepper
oil
flour
garlic
sugar
water
onion
olive
chicken
juice
milk
lemon
butter
egg
cheese
wheat
vegetable
vanilla
vinegar
parsley
honey
soy
wine
seeds
celery
rice
cinnamon
tomato
bread
eggs
onions
yeast
leaves
broth
tomatoes
cream
cloves
thyme
peeled
ginger
beans
soda
basil
mushrooms
apple
parmesan
yogurt
stock
bell
oats
sodium
beef
flakes
carrot
oregano
chocolate
cumin
paprika
sesame
mustard
spinach
corn
potatoes
coconut
carrots
nutmeg
cilantro
raisins
chili
syrup
peas
peanut
almond
walnuts
canned
lime
leaf
pineapple
margarine
cabbage
cucumber
broccoli
cornstarch
zucchini
coriander
paste
turkey
banana
almonds
nuts
maple
cheddar
cider
scallions
lettuce
dill'''
    
    ingList = ing.split()
    for i in range(1,len(ingList)+1):
       fake_data['ingID'].append('ING-'+ str(i))
       fake_data['name'].append(ingList[i-1])
    commit(fake_data,'ingredients')


def generateInstructions():

    fake_data = defaultdict(list)
    for i in range(1,NUM_RECIPE+1):
        fake_data['RecID'].append('RE-' + str(i))
        fake_data['IngreQua'].append(fake.pyint(1,10))
        for x in range(1,fake.pyint(2,5)):
            break

"""
Create Tables
"""


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
        Column('name',String(30)),
        Column('AllID',String(10),primary_key=True)
    )


    user_allergies = Table(
        'user_allergies',meta,
        Column('AccID',String(10),ForeignKey('accounts.AccID',ondelete='CASCADE'),primary_key=True ),
        Column('AllID',String(10),ForeignKey('allergies.AllID',ondelete='CASCADE'),primary_key=True )
    )
    desc = Table(
        'recipe_description',meta,
        Column('DescID',String(10),primary_key=True),
        Column('Desc',String(100))
    )
    recipe = Table(
        'recipes',meta,
        Column('RecID',String(10),primary_key=True),
        Column('title',String(50)),
        Column('calories',String(10)),
        Column('DescID',String(10),ForeignKey('recipe_description.DescID',ondelete='CASCADE')),
        Column('dateAdded',Date()),
        Column('prepTime',String(10)),
    )

    category = Table(
        'categories',meta,
        Column('RecID',String(10),ForeignKey('recipes.RecID',ondelete='CASCADE'),primary_key=True ),
        Column('category',String(20),primary_key=True)
    )

    image = Table(
        'image',meta,
        Column('ImgID',String(10),primary_key=True),
        Column('mealID',String(10),ForeignKey('meals.mealID',ondelete='CASCADE'))
    )

    meal = Table(
        'meals',meta,
        Column('mealID',String(10),primary_key=True),
        Column('title',String(20)),
        Column('servings',Integer()),
        Column('ImgID',String(10),ForeignKey('image.ImgID',ondelete='CASCADE'))
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
        Column('ingID',String(10),primary_key=True),
        Column('name',String(30)),

    )

    plan = Table(
        'meal_plan',meta,
        Column('planMID',String(10),primary_key = True),
        Column('Bfast',String(10),ForeignKey('categories.RecID',ondelete='CASCADE'),primary_key=True),
        Column('lunch',String(10),ForeignKey('categories.RecID',ondelete='CASCADE'),primary_key=True),
        Column('dinner',String(10),ForeignKey('categories.RecID',ondelete='CASCADE'),primary_key=True)
    )

    plan_assin = Table(
        'plan_assignments',meta,
        Column('AccID',ForeignKey('accounts.AccID',ondelete='CASCADE'),primary_key=True),
        Column('planMID',ForeignKey('meal_plan.planMID',ondelete='CASCADE'),primary_key=True)
    )

    
    meta.create_all(engine,checkfirst=True)


def createDB():
    if not database_exists(engine.url):
        create_database(engine.url)
    else:
        drop_database(engine.url)
        create_database(engine.url)

def commit(fake_data,table):
    df_fake_data = pd.DataFrame(fake_data)
    df_fake_data.to_sql(table,con=engine.connect(),index=False,if_exists='append')
    

if __name__ == '__main__':
    createDB()
    createTables()
    fakeAccount()
    fakeRecipe()
    generateAllergies()
    generateUserAllergies()
    generateCategories()
    generateIng()