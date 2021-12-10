from django.db import models
from django.contrib.auth.models import User


class DesignContest(models.Model):
	name = models.CharField(max_length=255)
	image = models.ImageField(upload_to='designContest', blank=True, null=True)
	guidelines = models.TextField(blank=False)
	reward = models.TextField(blank=True)
	contestDetails = models.TextField(blank=True)
	startDate = models.DateTimeField()
	endDate = models.DateTimeField()

	def __str__(self):
		return self.name


class ContestData(models.Model):
	description = models.TextField(blank=True)
	submitTime = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	designContest = models.ForeignKey(DesignContest, on_delete=models.CASCADE)
	
	class Meta:
		unique_together=['user', 'designContest']

	def __str__(self):
		return str('%s - %s' % (self.user, self.designContest))


class ContestImage(models.Model):
	image = models.ImageField(upload_to='designContest', blank=False, null=False)
	side = models.CharField(max_length=50, null=False, default='')
	contestData = models.ForeignKey(ContestData, on_delete=models.CASCADE)

	def __str__(self):
		return str('%s - %s' % (self.contestData, self.image))


'''
class ContestEnroll(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	designContest = models.ForeignKey(DesignContest, on_delete=models.CASCADE)
	
	class Meta:
		unique_together=['user', 'designContest']

	def __str__(self):
		return str('%s - %s' % (self.user, self.designContest))
'''