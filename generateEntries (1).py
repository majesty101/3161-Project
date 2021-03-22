import pandas as pd
from faker import Faker
from collections import defaultdict
from sqlalchemy import create_engine

fake=Faker()
fake_data = defaultdict(list)
allergy_list = ['Milk','Eggs','Nuts','Shellfish','Soy','Wheat','None']
def fakeAccount():
    for i in range(1000):
        fake_data["first_name"].append(fake.first_name())
        fake_data["last_name"].append(fake.last_name())
        fake_data['password'].append(fake.password(length=12))
        fake_data['allergies'].append(fake.word(word_list))
    df_fake_data = pd.DataFrame(fake_data)
    engine = create_engine('mysql://root:@localhost/testdb',echo=False)
    df_fake_data.to_sql('user',con=engine,index=False,if_exists='append')


if __name__ == '__main__':
    fakeAccount()