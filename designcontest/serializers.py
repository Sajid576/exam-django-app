from rest_framework import serializers
from rest_framework import exceptions

from .models import *
from customized_response.constants import *
from customized_response.response import *


class DesignContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignContest
        fields = '__all__'


class DesignContestListSerializer(serializers.ModelSerializer):
	class Meta:
		model = DesignContest
		fields = ['name']


class ContestImageSerializer(serializers.ModelSerializer):
	#image = serializers.SerializerMethodField()
	
	class Meta:
		model = ContestImage
		fields = ['side', 'image']

	#def get_image(self, contestimage):
	#	request = self.context.get('request')
	#	if contestimage.image and hasattr(contestimage, 'image'):
	#		image = contestimage.image.url
	#		return request.build_absolute_uri(image)
	#	return None


class ContestDataSerializer(serializers.ModelSerializer):
	images = serializers.ListField(child=serializers.ImageField(max_length=1000,
		allow_empty_file=False, use_url=False))
	side = serializers.CharField(max_length=50)
	
	class Meta:
		model = ContestData
		fields = ['images', 'side']
	
	def validate(self, attrs):
		image_list = attrs.get('images')
		for image in image_list:
			if image.size > 5*1024*1024:
				raise serializers.ValidationError(
					{'image_size': IMAGE_SIZE_ERROR})
		return super().validate(attrs)
			
	def save(self):
		user = self.context['request'].user
		contest = self.context['contest']
		
		try:
			contest_data, created = ContestData.objects.get_or_create(
				user=user, designContest=contest)
		except:
			resp = error_resp(DATA_NOT_FOUND, 'DATA_NOT_FOUND')
			raise exceptions.NotFound(resp)
		
		contest_data.description = ''
		contest_data.save()

		image_url_list = []
		image_list = self.context['request'].FILES.getlist('images')
		for image in image_list:
			img = ContestImage(image=image, side=self.validated_data['side'],
			contestData=contest_data)
			img.save()
			image_url = ContestImageSerializer(img, 
				context={'request': self.context['request']}).data
			image_url_list.append(image_url)
			break
		return image_url_list


'''
class ContestEnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestEnroll
        fields = '__all__'

class ContestDataRetrieveSerializer(ContestDataSerializer):
	class Meta:
		model = ContestData
		fields = ['description']

for image in image_list:
	try:
		img_str = 'designContest/'+ str(image) 
		img = ContestImage.objects.get(image=img_str, contestData=contest_data)
		image_url = ContestImageSerializer(img, 
			context={'request': self.context['request']}).data
		image_url_list.append(image_url)
		
	except:	
		img = ContestImage(image=image, contestData=contest_data)
		img.save()
		image_url = ContestImageSerializer(img, 
			context={'request': self.context['request']}).data
		image_url_list.append(image_url)
	
def save(self):
	description = self.validated_data['description']
	user = self.context['request'].user
	contest = self.context['contest']
	contest_data = ContestData(description=description, 
		user=user, designContest=contest)
	contest_data.save()
	
	image_url_list = []
	image_list = self.context['request'].FILES.getlist('images')
	for image in list(image_list):
		img = ContestImage(image=image, contestData=contest_data)
		img.save()
		image_url = ContestImageSerializer(img, 
			context={'request': self.context['request']}).data
		image_url_list.append(image_url)
	return image_url_list
'''