from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.

class VocabWord(models.Model):
    hiragana = models.TextField()
    kanji = models.TextField(blank=True)
    english_meaning = models.TextField()
    lesson_num = models.IntegerField()
    def __str__(self):
        return f"{self.hiragana}, {self.kanji},{self.english_meaning}, {self.lesson_num}"

def load_data():
    # have to get base dir because i have to include D:/ in my path locally
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, 'static', 'project', 'genki1vocab.csv')
    f = open(file_path, encoding='utf-8')
    f.readline()
    for row in f:
        fields = row.split(',')
        #some of the english translation contains a ',' so this will combine the , in the eng field
        if len(fields) > 4:
            fields[2] = ','.join(fields[2:-1])  
            fields = fields[:3] + [fields[-1]]
        result = VocabWord(
            hiragana = fields[0],
            kanji = fields[1],
            english_meaning = fields[2].strip(),
            lesson_num = int(fields[3]),
        )
        result.save()
        print(f'created : {result}')
    
        

class VocabList(models.Model):
    list_name = models.CharField(max_length= 20)
    
    #  1 user can have multiple list
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    
    #single list can contain many vocab and 
    #a vocabword can belong to many different vocablist I think for my app
    #in the case where user wants to create 2 differnt vocablist with some same words
    vocabulary_words = models.ManyToManyField(VocabWord)
    
    #list names are unique relative to the users and not globally
    class Meta:
        unique_together = ('list_name', 'user')
        
    def __str__(self):
        return f"{self.list_name}" 
    
class WrongList(models.Model):
    #each wrong list will be tied to a unique vocablist, as the wrong list will
    #be based on what the user got wrong, and they can only practice 1 list at a time.
    #there can be many wrong list, as I think I will have it generate each time they
    #go through vocablist once, and save it, so users can click to view all the wrong list
    #that was generated for that speific list. 
    #have to fulfull req of 2 FK ¯\_(ツ)_/¯
    vocabulary_list = models.ForeignKey(VocabList, on_delete=models.CASCADE)
    vocabulary_words = models.ManyToManyField(VocabWord) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list_number = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f"Wrong list # {self.list_number} in: {self.vocabulary_list.list_name}" 
