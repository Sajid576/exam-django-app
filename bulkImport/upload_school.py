import csv
import pandas as pd
from userInfo.models import School, Districts

read_file = pd.read_excel('../#Documents/SchoolListFL.xlsx', dtype=str)
read_file.to_csv('../#Documents/SchoolList.csv')

fhand = open('../#Documents/SchoolList.csv')
reader = csv.reader(fhand)
next(reader)
for row in reader:
    district, created = Districts.objects.get_or_create(name=row[2])
    school = School(name=row[4], schoolNumber=row[3], district_id=district.id)
    school.save()
