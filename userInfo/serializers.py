from datetime import datetime
from rest_framework import status
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.response import Response

from .models import *
from authentication.serializers import *


class ProfileSerializer(serializers.ModelSerializer):
    dateOfBirth = serializers.DateField(input_formats=['', '%d-%m-%Y'])

    class Meta:
        model = Profile
        exclude = ['user']

    def update(self):
        profile = Profile.objects.get(user_id=self.context.get('user_id')) 
        img = self.validated_data['image']
        
        if img is not None or self.context.get('remove').lower() == 'true':
            profile.image = self.validated_data['image']
        profile.firstName = self.validated_data['firstName']
        profile.lastName = self.validated_data['lastName']
        profile.dateOfBirth = self.validated_data['dateOfBirth']
        profile.bloodGroup = self.validated_data['bloodGroup']
        profile.birthId = self.validated_data['birthId']
        profile.nationalId = self.validated_data['nationalId']
        profile.taxId = self.validated_data['taxId']
        profile.height = self.validated_data['height']
        profile.religion = self.validated_data['religion']
        profile.nationality = self.validated_data['nationality']
        profile.citizenshipStatus = self.validated_data['citizenshipStatus']
        profile.dualCitizenship = self.validated_data['dualCitizenship']
        profile.save()


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    #dateOfBirth = serializers.DateField(format='%d-%m-%Y')
    
    class Meta:
        model = Profile
        exclude = ['id', 'user', 'dateOfBirth', 'bloodGroup', 'height']

    def to_representation(self, instance):
        rep = super(ProfileRetrieveSerializer, self).to_representation(instance)
        try:
            rep['nationality'] = instance.nationality.name
        except:
            rep['nationality'] = None
        try:
            rep['religion'] = instance.get_religion_display()
        except:
            rep['religion'] = None
        try:
            rep['citizenshipStatus'] = instance.get_citizenshipStatus_display()
        except:
            rep['citizenshipStatus'] = None
        return rep
    

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['firstName', 'lastName', 'image', 'nationality']
        
    def to_representation(self, instance):
        rep = super(PersonalInfoSerializer, self).to_representation(instance)
        try:
            rep['nationality'] = instance.nationality.name
        except:
            rep['nationality'] = None 
        return rep


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model= Address
        exclude = ['id', 'user']

    def save(self):
        address, created = Address.objects.get_or_create(
            user_id=self.context['user_id'],
            isPermanentAddress=self.validated_data['isPermanentAddress'])
        
        address.country = self.validated_data['country']
        address.division = self.validated_data['division']
        address.district = self.validated_data['district']
        address.thana = self.validated_data['thana']
        address.village = self.validated_data['village']
        address.postOffice = self.validated_data['postOffice'] 
        address.roadNo = self.validated_data['roadNo']
        #if self.validated_data['isPermanentAddress']:
        address.sameAsPresentAddress = self.validated_data['sameAsPresentAddress']
        #else:
        #    address.sameAsPresentAddress = None
        address.save()


class AddressRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model= Address
        exclude = ['id', 'user']
    
    def to_representation(self, instance):
        rep = super(AddressRetrieveSerializer, self).to_representation(instance)
        try:
            rep['postOffice'] = instance.postOffice.name
        except:
            rep['postOffice'] = None
        try:
            rep['village'] = instance.village.name
        except:
            rep['village'] = None
        try:
            rep['thana'] = instance.thana.name
        except:
            rep['thana'] = None
        try:
            rep['district'] = instance.district.name
        except:
            rep['district'] = None
        try:
            rep['division'] = instance.division.name
        except:
            rep['division'] = None
        try:
            rep['country'] = instance.country.name
        except:
            rep['country'] = None
        return rep
    

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = '__all__'   


class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = ['id', 'name']


class DivisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ['id', 'name']  


class DistrictsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Districts
        fields = ['id', 'name']


class ThanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thana
        fields = ['id', 'name']  


class PostOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostOffice
        fields = ['name']


class VillagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ['name']  


class UserMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMobile
        fields = ['mobile', 'primary', 'code']

    def create(self):
        if self.validated_data['mobile'].startswith('+880') or self.validated_data['mobile'].startswith('+1'):
            user_mobile = UserMobile.objects.create(mobile=self.validated_data['mobile'], 
            primary=False, code=self.validated_data['code'], 
            user_id=self.context['user_id']
            )
        else:
            return -3
        
        #if self.validated_data['primary']:
        #    user_mobiles = UserMobile.objects.filter(primary=True,
        #    user_id=self.context['user_id']).exclude(id=user_mobile.id) 
        #    for mobile in user_mobiles:
        #        mobile.primary = False
        #        mobile.save()
    
    def update(self):
        if self.validated_data['mobile'].startswith('+880') or self.validated_data['mobile'].startswith('+1'):
            try:
                user_mobile = UserMobile.objects.get(id=self.context['id'])
                if user_mobile.user.id != self.context['user_id']:
                    return -2

                user_mobile.primary = False
                user_mobile.code = self.validated_data['code']
                user_mobile.mobile = self.validated_data['mobile']
                user_mobile.save()
            except:
                return -1
        else:
            return -3
        #if self.validated_data['primary']:
        #    user_mobiles = UserMobile.objects.filter(primary=True,
        #    user_id=self.context['user_id']).exclude(id=user_mobile.id) 
        #    for mobile in user_mobiles:
        #        mobile.primary = False
        #        mobile.save()


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmail
        fields = ['email', 'primary']

    def create(self):
        user_email = UserEmail.objects.create(email=self.validated_data['email'], 
        primary=False,
        user_id=self.context['user_id']
        )
        
        #if self.validated_data['primary']:
        #    user_emails = UserEmail.objects.filter(primary=True,
        #    user_id=self.context['user_id']).exclude(id=user_email.id) 
        #    for email in user_emails:
        #        email.primary = False
        #        email.save()

    def update(self):
        try:
            user_email = UserEmail.objects.get(id=self.context['id'])
            if user_email.user.id != self.context['user_id']:
                return -2
            
            user_email.primary = False
            user_email.email = self.validated_data['email']
            user_email.save()
        except:
            return -1
        
        #if self.validated_data['primary']:
        #    user_emails = UserEmail.objects.filter(primary=True,
        #    user_id=self.context['user_id']).exclude(id=user_email.id) 
        #    for email in user_emails:
        #        email.primary = False
        #        email.save()


class FatherInfoAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = FatherInfo
        exclude = ['user']

    def create(self):
        FatherInfo.objects.create(
            fatherName = self.validated_data['fatherName'],
            fatherJob = self.validated_data['fatherJob'],
            fatherNationality = self.validated_data['fatherNationality'],
            user_id = self.context['user_id']
        )

    def update(self):
        father_info = FatherInfo.objects.get(user_id=self.context['user_id'])
        father_info.fatherName = self.validated_data['fatherName']
        father_info.fatherJob = self.validated_data['fatherJob']
        father_info.fatherNationality = self.validated_data['fatherNationality']
        father_info.save()


class MotherInfoAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotherInfo
        exclude = ['user']

    def create(self):        
        MotherInfo.objects.create(
            motherName = self.validated_data['motherName'],
            motherJob = self.validated_data['motherJob'],
            motherNationality = self.validated_data['motherNationality'],
            user_id = self.context['user_id']    
        )
    
    def update(self):
        mother_info = MotherInfo.objects.get(user_id=self.context['user_id'])
        mother_info.motherName = self.validated_data['motherName']
        mother_info.motherJob = self.validated_data['motherJob']
        mother_info.motherNationality = self.validated_data['motherNationality']
        mother_info.save()


class SpouseInfoAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpouseInfo
        exclude = ['user']

    def create(self):
        SpouseInfo.objects.create(
            spouseName = self.validated_data['spouseName'],    
            spouseJob = self.validated_data['spouseJob'],
            spouseNationality = self.validated_data['spouseNationality'],
            user_id = self.context['user_id']
        )

    def update(self):
        spouse_info = SpouseInfo.objects.get(user_id=self.context['user_id'])
        spouse_info.spouseName = self.validated_data['spouseName']
        spouse_info.spouseJob = self.validated_data['spouseJob']
        spouse_info.spouseNationality = self.validated_data['spouseNationality']
        spouse_info.save()


class FatherInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FatherInfo
        exclude = ['id', 'user']

    def to_representation(self, instance):
        rep = super(FatherInfoSerializer, self).to_representation(instance)
        try:
            rep['fatherJob'] = instance.fatherJob.name
        except:
            rep['fatherJob'] = None
        try:
            rep['fatherNationality'] = instance.fatherNationality.name
        except:
            rep['fatherNationality'] = None
        return rep


class MotherInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotherInfo
        exclude = ['id', 'user']
    
    def to_representation(self, instance):
        rep = super(MotherInfoSerializer, self).to_representation(instance)
        try:
            rep['motherJob'] = instance.motherJob.name
        except:
            rep['motherJob'] = None
        try:
            rep['motherNationality'] = instance.motherNationality.name
        except:
            rep['motherNationality'] = None
        return rep


class SpouseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpouseInfo
        exclude = ['id', 'user']

    def to_representation(self, instance):
        rep = super(SpouseInfoSerializer, self).to_representation(instance)
        try:
            rep['spouseJob'] = instance.spouseJob.name    
        except:
            rep['spouseJob'] = None
        try:
            rep['spouseNationality'] = instance.spouseNationality.name
        except:
            rep['spouseNationality'] = None
        return rep


class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['name']


class SchoolDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'
    
    def to_representation(self, instance):
        rep = super(SchoolDetailSerializer, self).to_representation(instance)
        try:
            rep['district'] = instance.district.name
        except:
            rep['district'] = None
        try:
            rep['country'] = instance.country.name
        except:
            rep['country'] = None
        return rep


class SchoolInfoRetrieveSerializer(serializers.ModelSerializer):
    className = serializers.ChoiceField(choices=CLASSRANGE, source='get_className_display', allow_null=True)
    boardName = serializers.ChoiceField(choices=BOARD, source='get_boardName_display', allow_null=True)
    field = serializers.ChoiceField(choices=GROUP, source='get_field_display', allow_null=True)
    
    class Meta:
        model = SchoolInfo
        exclude =  ['user']
    
    def to_representation(self, instance):
        rep = super(SchoolInfoRetrieveSerializer, self).to_representation(instance)
        try:
            rep['schoolName'] = instance.schoolName.name
        except:
            rep['schoolName'] = None 
        return rep


class SchoolInfoSerializerForLandingProfile(serializers.ModelSerializer):
    className = serializers.ChoiceField(choices=CLASSRANGE,source= 'get_className_display',allow_null=True)
    boardName = serializers.ChoiceField(choices=BOARD,source= 'get_boardName_display',allow_null=True)
    field = serializers.ChoiceField(choices=GROUP, source='get_field_display', allow_null=True)

    class Meta:
        model = SchoolInfo
        exclude =  ['grade', 'activites', 'description', 'completeness', 'user']

    def to_representation(self, instance):
       rep = super(SchoolInfoSerializerForLandingProfile, self).to_representation(instance)
       try:
           rep['schoolName'] = instance.schoolName.name
       except:
           rep['schoolName'] = None 
       return rep


class SchoolInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolInfo
        exclude =  []
    
    def validate(self, attrs):
        user = attrs.get('user')
        start_date = attrs.get('startDate') 
        end_date = attrs.get('endDate')
        class_name = attrs.get('className')
        school_name = attrs.get('schoolName')
        
        if class_name is None or class_name < 9:
            attrs['field'] = None
        field = attrs['field']
        
        if class_name != 10:
            attrs['grade'] = None
        
        if self.context.get('this_id'): 
            all_schools = SchoolInfo.objects.filter(user=user)
            schools = all_schools.exclude(id=self.context.get('this_id'))
            current_school = all_schools.filter(id=self.context.get('this_id'))[0]
            if class_name == 10 and field != current_school.field:
                raise serializers.ValidationError({'field': FIELD_UPDATE_ERROR})
        else:
            schools = SchoolInfo.objects.filter(user=user)
            
        for school in schools:
            if school.startDate is not None and school.endDate is not None:
                if start_date is not None and start_date >= school.startDate and start_date <= school.endDate:
                    raise serializers.ValidationError({'startDate': DATE_ERROR})
            
                if end_date is not None and end_date >= school.startDate and end_date <= school.endDate:
                    raise serializers.ValidationError({'endDate': DATE_ERROR})
            
            if school.currentStudent:
                attrs['currentStudent'] = False
            
            if class_name is not None and school.className is not None and class_name == school.className:
                raise serializers.ValidationError({'className': CLASS_ERROR})
        
        colleges = CollegeInfo.objects.filter(user=user)
        for college in colleges:
            if college.startDate is not None and college.endDate is not None:
                if start_date is not None and start_date >= college.startDate and start_date <= college.endDate:
                    raise serializers.ValidationError({'startDate': DATE_ERROR})
            
                if end_date is not None and end_date >= college.startDate and end_date <= college.endDate:
                    raise serializers.ValidationError({'endDate': DATE_ERROR})
            
            if field is not None and field == 3 and (college.field == 1 or college.field == 2):
                raise serializers.ValidationError({'field': FIELD_ERROR})
        
            elif field is not None and field == 2 and college.field == 1:
                raise serializers.ValidationError({'field': FIELD_ERROR})

        universities = UniversityInfo.objects.filter(user=user)
        for university in universities:
            if university.startDate is not None and university.endDate is not None:
                if start_date is not None and start_date >= university.startDate and start_date <= university.endDate:
                    raise serializers.ValidationError({'startDate': DATE_ERROR})
            
                if end_date is not None and end_date >= university.startDate and end_date <= university.endDate:
                    raise serializers.ValidationError({'endDate': DATE_ERROR})

        if colleges.exists() or universities.exists():
            attrs['currentStudent'] = False

        if class_name is not None and school_name is not None and school_name.startClass is not None and school_name.endClass is not None and (class_name < school_name.startClass or class_name > school_name.endClass):
            raise serializers.ValidationError({'className': CLASS_BOUND_ERROR})
        
        if start_date is not None and end_date is not None and end_date < start_date:
            raise serializers.ValidationError({'endDate': END_DATE_BOUND_ERROR})
        
        if attrs['currentStudent'] and end_date is not None and end_date < datetime.utcnow().date():
            raise serializers.ValidationError({'currentStudent': CURRENT_STUDENT_ERROR})
        
        return super().validate(attrs)


class CollegeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['name', 'scienceDept', 'commerceDept', 'artsDept']


class CollegeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'    
    
    def to_representation(self, instance):
        rep = super(CollegeDetailSerializer, self).to_representation(instance)
        try:
            rep['country'] = instance.country.name
        except:
            rep['country'] = None
        return rep


class CollegeInfoRetrieveSerializer(serializers.ModelSerializer):
    className = serializers.ChoiceField(choices=COLLEGE_CLASSRANGE,source='get_className_display', allow_null=True)
    boardName = serializers.ChoiceField(choices=BOARD,source='get_boardName_display', allow_null=True)
    field = serializers.ChoiceField(choices=GROUP, source='get_field_display', allow_null=True)

    class Meta:
        model = CollegeInfo
        exclude =  ['user']

    def to_representation(self, instance):
        rep = super(CollegeInfoRetrieveSerializer, self).to_representation(instance)
        try:
            rep['collegeName'] = instance.collegeName.name
        except:
            rep['collegeName'] = None 
        return rep


class CollegeInfoSerializerForLandingProfile(serializers.ModelSerializer):
    className = serializers.ChoiceField(choices=COLLEGE_CLASSRANGE,source= 'get_className_display',allow_null=True)
    boardName = serializers.ChoiceField(choices=BOARD,source= 'get_boardName_display',allow_null=True)
    field = serializers.ChoiceField(choices=GROUP, source='get_field_display', allow_null=True)

    class Meta:
        model = CollegeInfo
        exclude =  ['grade', 'activites', 'description', 'completeness', 'user']

    def to_representation(self, instance):
        rep = super(CollegeInfoSerializerForLandingProfile, self).to_representation(instance)
        try:
            rep['collegeName'] = instance.collegeName.name
        except:
            rep['collegeName'] = None 
        return rep


class CollegeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeInfo
        exclude =  []

    def validate(self, attrs):
        user = attrs.get('user')
        start_date = attrs.get('startDate')
        end_date = attrs.get('endDate')
        class_name = attrs.get('className')
        college_name = attrs.get('collegeName')
        field = attrs.get('field')
        
        if class_name != 2:
            attrs['grade'] = None

        if self.context.get('this_id'):
            all_colleges = CollegeInfo.objects.filter(user=user)
            colleges = all_colleges.exclude(id=self.context.get('this_id'))
            current_college = all_colleges.filter(id=self.context.get('this_id'))[0]
            if class_name == 2 and field != current_college.field:
                raise serializers.ValidationError({'field': FIELD_UPDATE_ERROR})
        else:
            colleges = CollegeInfo.objects.filter(user=user)
        
        schools = SchoolInfo.objects.filter(user=user)
        for school in schools:
            if school.currentStudent:
                raise serializers.ValidationError({'college_add_error': COLLEGE_ADD_ERROR})
            
            if school.startDate is not None and school.endDate is not None:
                if start_date is not None and start_date >= school.startDate and start_date <= school.endDate:
                    raise serializers.ValidationError({'startDate': DATE_ERROR})
            
                if end_date is not None and end_date >= school.startDate and end_date <= school.endDate:
                    raise serializers.ValidationError({'endDate': DATE_ERROR})

            if field is not None and field == 1 and (school.field == 2 or school.field == 3):
                raise serializers.ValidationError({'field': FIELD_ERROR})
        
            if field is not None and field == 2 and school.field == 3:
                raise serializers.ValidationError({'field': FIELD_ERROR})
        
        for college in colleges:
            if college.startDate is not None and college.endDate is not None:
                if start_date is not None and start_date >= college.startDate and start_date <= college.endDate:
                    raise serializers.ValidationError({'startDate': DATE_ERROR})
            
                if end_date is not None and end_date >= college.startDate and end_date <= college.endDate:
                    raise serializers.ValidationError({'endDate': DATE_ERROR})

            if college.currentStudent:
                attrs['currentStudent'] = False

            if class_name is not None and college.className is not None and class_name == college.className:
                raise serializers.ValidationError({'className': CLASS_ERROR})
        
        universities = UniversityInfo.objects.filter(user=user)
        for university in universities:
            if university.startDate is not None and university.endDate is not None:
                if start_date is not None and start_date >= university.startDate and start_date <= university.endDate:
                    raise serializers.ValidationError({'startDate': DATE_ERROR})
            
                if end_date is not None and end_date >= university.startDate and end_date <= university.endDate:
                    raise serializers.ValidationError({'endDate': DATE_ERROR})

        if college_name is not None and field is not None:
            if field == 1 and not college_name.scienceDept:
               raise serializers.ValidationError({'field': FIELD_BOUND_ERROR})
            
            elif field == 2 and not college_name.commerceDept:
               raise serializers.ValidationError({'field': FIELD_BOUND_ERROR})
            
            elif field == 3 and not college_name.artsDept:
               raise serializers.ValidationError({'field': FIELD_BOUND_ERROR})
        
        if start_date is not None and end_date is not None and end_date < start_date:
            raise serializers.ValidationError({'endDate': END_DATE_BOUND_ERROR})
        
        if attrs['currentStudent'] and end_date is not None and end_date < datetime.utcnow().date():
            raise serializers.ValidationError({'currentStudent': CURRENT_STUDENT_ERROR})

        if universities.exists():
            attrs['currentStudent'] = False
        
        return super().validate(attrs)


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields =  ["name"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields =  ["name"]


class UniversityDepartmentSerializer(serializers.ModelSerializer):
    department_set = DepartmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = University
        fields =  ["name", "department_set"]


class UniversityInfoRetrieveSerializer(serializers.ModelSerializer):
    university = UniversitySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    
    class Meta:
        model = UniversityInfo
        exclude =  []


class UniversityInfoSerializerForLandingProfile(serializers.ModelSerializer):
    class Meta:
        model = UniversityInfo
        exclude =  ['grade', 'activites', 'description', 'completeness', 'user']
    
    def to_representation(self, instance):
        rep = super(UniversityInfoSerializerForLandingProfile, self).to_representation(instance)
        try:
            rep['university'] = instance.university.name
        except:
            rep['university'] = None
        try:
            rep['department'] = instance.department.name
        except:
           rep['department'] = None 
        return rep


class UniversityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityInfo
        exclude =  []
    '''
    def validate(self, attrs):
        user = attrs.get('user')

        schools = SchoolInfo.objects.filter(user=user)
        for school in schools:
            if school.currentStudent:
                raise serializers.ValidationError({'uni_add_error': UNI_ADD_ERROR})
        
        colleges = CollegeInfo.objects.filter(user=user)
        for college in colleges:
            if college.currentStudent:
                raise serializers.ValidationError({'uni_add_error': UNI_ADD_ERROR})
        
        return super().validate(attrs)
    '''

'''Previous Team
class CurrenciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currencies
        fields = '__all__'

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = '__all__'                  
'''