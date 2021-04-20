from django.db import models

# Create your models here.
class Ticker(models.Model):
   SENTIMENT = (
      ('Bullish', 'Bullish'),
      ('Bearish', 'Bearish'),
      ('Neutral', 'Neutral'),
      )

   ticker = models.CharField(max_length=200)
   date_posted = models.DateTimeField()
   sentiment = models.CharField(max_length=200, choices = SENTIMENT)
   sentence = models.TextField()

   def __str__(self):
      return ("Ticker: " + str(self.ticker) + " Date: " + str(self.date_posted) + " Sentiment: " + str(self.sentiment))