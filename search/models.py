from django.db import models

# Create your models here.
class RawText(models.Model):
    title = models.CharField(max_length=20)
    abstract = models.CharField(max_length=128)
    index_field = models.CharField(db_column='index_', max_length=50, primary_key=True)  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'raw_text'


class WordDictionary(models.Model):
    index_field = models.CharField(db_column='index_', max_length=20, primary_key=True)  # Field renamed because it ended with '_'.
    value_field = models.CharField(db_column='value_', max_length=128)  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'word_dictionary'
