from django.contrib import admin
from .models import VocabWord, VocabList, WrongList
# Register your models here.
admin.site.register(VocabWord)
admin.site.register(VocabList)
admin.site.register(WrongList)
