from datetime import date
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxValueValidator, MinValueValidator


RELIGIONS = (
    (1, 'Islam'),
    (2, 'Christianity'),
    (3, 'Hinduism'),
    (4, 'Buddhism'),
    (5, 'Other'),
)

CITIZENSHIP_STATUS = (
    (1, 'BIRTH'),
    (2, 'PARENTAGE'),
    (3, 'MIGRATION'),
    (4, 'NATURALIZATION'),
    (5, 'OTHERS')
)

DEGREE = (
    (1, 'PRIMARY'),
    (2, 'SSC'),
    (3, 'HSC'),
    (4, 'BACHELOR'),
    (5, 'MASTERS'),
    (6, 'OTHERS'),
    #(7, '')
)

GROUP = (
    (1, 'SCIENCE'),
    (2, 'COMMERCE'),
    (3, 'ARTS')
)

CLASSRANGE = (
    (1, 'class 1'),
    (2, 'class 2'),
    (3, 'class 3'),
    (4, 'class 4'),
    (5, 'class 5'),
    (6, 'class 6'),
    (7, 'class 7'),
    (8, 'class 8'),
    (9, 'class 9'),
    (10, 'class 10')
    #(11, '')
)

COLLEGE_CLASSRANGE = (
    #(0, ''),
    (1, "class 11"),
    (2, "class 12")
)

BOARD = (
    (1, 'DHAKA'),
    (2, 'CHITTAGONG'),
    (3, 'CUMILLA'),
    (4, 'RAJSHAHI'),
    (5, 'DINAJPUR'),
    (6, 'BARISHAL'),
    (7, 'SYLHET'),
    (8, 'MYMENSINGH')
    #(9, '')
)

class Countries(models.Model):
    name = models.CharField(max_length=255)
    countryCode = models.CharField(max_length=255, null=True)
    defaultCurrency = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name   


class Division(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(to=Countries, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "Division"

    def __str__(self):
        return self.name   


class Districts(models.Model):
    name = models.CharField(max_length=255)
    division = models.ForeignKey(to=Division, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "Districts"

    def __str__(self):
        return self.name   


class Thana(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey(to=Districts, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "Thana"

    def __str__(self):
        return self.name   


class Village(models.Model):
    name = models.CharField(max_length=255)
    thana = models.ForeignKey(to=Thana, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "Village"

    def __str__(self):
        return self.name   


class PostOffice(models.Model):
    name = models.CharField(max_length=255)
    thana = models.ForeignKey(to=Thana, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "PostOffice"

    def __str__(self):
        return self.name   


class Nationality(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return str('%s' % (self.name))


class Profile(models.Model):
    image = models.ImageField(upload_to='profilePics', blank=True, null=True, max_length=512)
    dateOfBirth = models.DateField(null=True)
    bloodGroup = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255, blank=True, null=True)
    birthId = models.CharField(max_length=255, blank=True, null=True)
    nationalId = models.CharField(max_length=255, blank=True, null=True)
    taxId = models.CharField(max_length=255, blank=True, null=True)
    height = models.CharField(max_length=255, blank=True, null=True)
    religion = models.IntegerField(choices=RELIGIONS, null=True)
    nationality = models.ForeignKey(to=Nationality, on_delete=models.SET_NULL, null=True)
    citizenshipStatus = models.IntegerField(choices=CITIZENSHIP_STATUS, null=True)
    dualCitizenship = models.BooleanField(default=False, null=True)
    
    def __str__(self):
        return str('%s' % (self.user))


class Address(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    country = models.ForeignKey(to=Countries, on_delete=models.SET_NULL, null=True)
    division = models.ForeignKey(to=Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(to=Districts, on_delete=models.SET_NULL, null=True)
    thana = models.ForeignKey(to=Thana, on_delete=models.SET_NULL, null=True)
    village = models.ForeignKey(to=Village, on_delete=models.SET_NULL,null=True)
    postOffice = models.ForeignKey(to=PostOffice, on_delete=models.SET_NULL, null=True)
    roadNo = models.CharField(max_length=255, blank=True, null=True)
    isPermanentAddress = models.BooleanField()
    sameAsPresentAddress = models.BooleanField(default=False, null=True)
    
    class Meta:
        unique_together=['user', 'isPermanentAddress']
    
    def __str__(self):
        return str('%s - %s' % (self.user, self.isPermanentAddress))


class UserMobile(models.Model):
    mobile = PhoneNumberField(blank=False, null=False, unique=True)
    primary = models.BooleanField(default=False)
    code = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    
    def __str__(self):
        return str('%s - %s' % (self.user, self.mobile))


class UserEmail(models.Model):
    email = models.EmailField(blank=False) 
    primary = models.BooleanField(default=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return str('%s - %s' % (self.user, self.email))


class Profession(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return str('%s' % (self.name))


class FatherInfo(models.Model):
    fatherName = models.CharField(max_length=254, blank=True)
    fatherJob = models.ForeignKey(to=Profession, null=True, on_delete=models.SET_NULL)
    fatherNationality = models.ForeignKey(to=Nationality, null=True, on_delete=models.SET_NULL)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return str('%s - %s' % (self.user, self.fatherName))


class MotherInfo(models.Model):    
    motherName = models.CharField(max_length=254, blank=True)
    motherJob = models.ForeignKey(to=Profession, null=True, on_delete=models.SET_NULL)
    motherNationality = models.ForeignKey(to=Nationality, null=True, on_delete=models.SET_NULL)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return str('%s - %s' % (self.user, self.motherName))


class SpouseInfo(models.Model):
    spouseName = models.CharField(max_length=254, blank=True)
    spouseJob = models.ForeignKey(to=Profession, null=True, on_delete=models.SET_NULL)
    spouseNationality = models.ForeignKey(to=Nationality, null=True, on_delete=models.SET_NULL)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return str('%s - %s' % (self.user, self.spouseName))


class School(models.Model):
    image = models.ImageField(upload_to='SchoolPics', blank=True, null=True, max_length=255)
    name = models.CharField(max_length=255)
    schoolNumber = models.CharField(max_length=255, null=True)
    startClass = models.IntegerField(null=True)
    endClass = models.IntegerField(null=True)
    establishDate = models.DateField(null=True)
    district = models.ForeignKey(Districts, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class SchoolInfo(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    schoolName = models.ForeignKey(to=School, on_delete=models.SET_NULL, null=True)
    className = models.IntegerField(choices=CLASSRANGE, null=True)
    boardName = models.IntegerField(choices=BOARD, null=True)
    field = models.IntegerField(choices=GROUP, null=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    currentStudent = models.BooleanField(default=False)
    grade = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    null=True)
    activites = models.CharField(max_length=254, blank=True)
    description = models.CharField(max_length=500, blank=True)
    completeness = models.IntegerField(null=True)

    class Meta:
        unique_together = ['user', 'schoolName']

    def __str__(self):
        return str('%s - %s' % (self.user, self.schoolName))


class College(models.Model):
    image = models.ImageField(upload_to='CollegePics', blank=True, null=True, max_length=255)
    name = models.CharField(max_length=255)
    establishDate = models.DateField(null=True)
    scienceDept = models.BooleanField(default=True)
    commerceDept = models.BooleanField(default=True)
    artsDept = models.BooleanField(default=True)
    country = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class CollegeInfo(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    collegeName = models.ForeignKey(to=College, on_delete=models.SET_NULL, null=True)
    className = models.IntegerField(choices=COLLEGE_CLASSRANGE, null=True)
    boardName = models.IntegerField(choices=BOARD, null=True)
    field = models.IntegerField(choices=GROUP, null=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    currentStudent = models.BooleanField(default=False)
    grade = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], 
    null=True)
    activites = models.CharField(max_length=254, blank=True)
    description = models.CharField(max_length=500, blank=True)
    completeness = models.IntegerField(null=True)
    
    class Meta:
        unique_together = ['user', 'collegeName']

    def __str__(self):
        return str('%s - %s' % (self.user, self.collegeName))


class University(models.Model):
    name = models.CharField(max_length=254)
    image = models.ImageField(upload_to='universityPics', blank=True, null=True, max_length=512)
    country = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=254)
    university = models.ForeignKey(to=University, on_delete=models.SET_NULL, default=None, null=True)
    
    def __str__(self):
        return str('%s - %s' % (self.university, self.name))


class UniversityInfo(models.Model):
    university = models.ForeignKey(to=University, on_delete=models.SET_NULL, null = True)
    department =  models.ForeignKey(to=Department,on_delete=models.SET_NULL, null =True)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    startDate = models.DateField(null = True)
    endDate = models.DateField(null=True)
    currentStudent = models.BooleanField(default=False)
    grade = models.FloatField(null= True)
    activites = models.CharField(max_length=254, blank=True)
    description = models.CharField(max_length=500, blank=True)
    completeness = models.IntegerField(null=True)

    def __str__(self):
        return str('%s - %s' % (self.user, self.university))

class Cities(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(to=Countries, on_delete=models.CASCADE, null=True)
    state = models.CharField(max_length=255)
    createdAT = models.DateTimeField(default=timezone.now)
    updatedAt = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name

class Configuration(models.Model):
    name = models.CharField(max_length=255)
    organizationName = models.CharField(max_length=255)
    domainName = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    metaTitle = models.TextField(blank=False)
    metaDesc = models.TextField(blank=False)
    timezone = models.CharField(max_length=100)
    author = models.CharField(max_length=255)
    sms = models.BooleanField(default=False)
    emailNotification = models.BooleanField(default=False)
    guestLogin = models.BooleanField(default=False)
    frontEnd = models.BooleanField(default=False)
    slides = models.SmallIntegerField(blank=False)
    translate = models.SmallIntegerField(default=0)
    paidExam = models.SmallIntegerField(default=1)
    leaderBoard = models.BooleanField(default=True)
    contact = models.TextField(blank=False)
    photo = models.CharField(max_length=100)
    createdAt = models.DateField(default=date.today)
    modifiedAt = models.DateField(default=date.today)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    message = models.TextField(max_length=5000)
    createdAt = models.DateField(default=date.today)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    createdAt = models.DateField(default=date.today)
    updatedAt = models.DateField(default=date.today)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
             
class Currencies(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    sign = models.CharField(max_length=255)
    usdConversionAmount = models.IntegerField()
    expiredAt = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.title

class Social(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    socialName = models.CharField(max_length=255)
    socialUrl = models.CharField(max_length=255)
    socialIcon = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Socials"

    def __str__(self):
        return self.socialName            
