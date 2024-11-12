from django.db import models
import csv
from django.db import transaction
from datetime import datetime
from django.conf import settings
import os
# Create your models here.
class Voter(models.Model):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    str_number = models.CharField(max_length=10)
    str_name = models.CharField(max_length=100)
    apt_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=20)
    precinct_number = models.CharField(max_length=10)
    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Precinct {self.precinct_number}"
    
def load_data(file_path=os.path.join(settings.BASE_DIR, 'voter_analytics', 'static', 'newton_voters.csv')):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        with transaction.atomic():
            for row in reader:
                Voter.objects.create(
                    last_name=row['Last Name'],
                    first_name=row['First Name'],
                    str_number=row['Residential Address - Street Number'],
                    str_name=row['Residential Address - Street Name'],
                    apt_number=row.get('Residential Address - Apartment Number', ''),
                    zip_code=row['Residential Address - Zip Code'],
                    date_of_birth=datetime.strptime(row['Date of Birth'], '%Y-%m-%d'),
                    date_of_registration=datetime.strptime(row['Date of Registration'], '%Y-%m-%d'),
                    party_affiliation=row['Party Affiliation'],
                    precinct_number=row['Precinct Number'],
                    v20state=row['v20state'] == 'TRUE',
                    v21town=row['v21town'] == 'TRUE',
                    v21primary=row['v21primary'] == 'TRUE',
                    v22general=row['v22general'] == 'TRUE',
                    v23town=row['v23town'] == 'TRUE',
                    voter_score=int(row['voter_score'])
                )