from customized_response.constants import *


def error_check(restdict):
	if 'username' in restdict.keys():
		return error_resp(USR_EXIST, 'USR_EXIST')

	elif 'email' in restdict.keys():
		return error_resp(EMAIL_IN_USE, 'EMAIL_IN_USE')

	elif 'password' in restdict.keys():
		return error_resp(PASS_SHORT, 'PASS_SHORT')
	
	elif 'new_password' in restdict.keys():
		return error_resp(PASS_SHORT, 'PASS_SHORT')

	elif 'confirm' in restdict.keys():
		return error_resp(PASS_NOT_MATCH, 'PASS_NOT_MATCH')

	elif 'first_name' in restdict.keys():
		return error_resp(INVALID_FIRST, 'INVALID_FIRST')

	elif 'last_name' in restdict.keys():
		return error_resp(INVALID_LAST, 'INVALID_LAST')

	elif 'fullName' in restdict.keys():
		return error_resp(EMPTY_FIELD.format('FullName'), 'EMPTY_FIELD')

	elif 'bloodGroup' in restdict.keys():
		return error_resp(EMPTY_FIELD.format('BloodGroup'), 'EMPTY_FIELD')

	elif 'address' in restdict.keys():
		return error_resp(EMPTY_FIELD.format('Address'), 'EMPTY_FIELD')

	elif 'description' in restdict.keys():
		return error_resp(EMPTY_FIELD.format('description'), 'EMPTY_FIELD')

	elif 'images' in restdict.keys():
		return error_resp(EMPTY_FIELD.format('images'), 'EMPTY_FIELD')

	elif 'image_size' in restdict.keys():
		return error_resp(IMAGE_SIZE_ERROR, 'IMAGE_SIZE_ERROR')

	elif 'side' in restdict.keys():
		return error_resp(EMPTY_FIELD.format('side'), 'EMPTY_FIELD')
		
	elif 'dateOfBirth' in restdict.keys():
		return error_resp(DATE_FORMAT_ERROR, 'DATE_FORMAT_ERROR')

	elif 'mobile' in restdict.keys():
		if restdict['mobile'][0].code == 'invalid_phone_number':
			return error_resp(INVALID_MOBILE_NUM, 'INVALID_MOBILE_NUM')
		elif restdict['mobile'][0].code == 'unique':
			return error_resp(MOBILE_NUM_EXISTS, 'MOBILE_NUM_EXISTS')
	
	elif 'primary' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('primary'), 'INVALID_CHOICE')
	
	elif 'religion' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('religion'), 'INVALID_CHOICE')
	
	elif 'citizenshipStatus' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('citizenshipStatus'), 'INVALID_CHOICE')
	
	elif 'nationality' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('nationality'), 'INVALID_CHOICE')
	
	elif 'country' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('country'), 'INVALID_CHOICE')
	
	elif 'division' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('division'), 'INVALID_CHOICE')
	
	elif 'district' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('district'), 'INVALID_CHOICE')
	
	elif 'thana' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('thana'), 'INVALID_CHOICE')
	
	elif 'village' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('village'), 'INVALID_CHOICE')
	
	elif 'postOffice' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('postOffice'), 'INVALID_CHOICE')
	
	elif 'isPermanentAddress' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('isPermanentAddress'), 'INVALID_CHOICE')
	
	elif 'sameAsPresentAddress' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('sameAsPresentAddress'), 'INVALID_CHOICE')
		
	elif 'startDate' in restdict.keys():
		return error_resp(restdict['startDate'][0], 'INVALID_CHOICE')

	elif 'endDate' in restdict.keys():
		return error_resp(restdict['endDate'][0], 'INVALID_CHOICE')
	
	elif 'schoolName' in restdict.keys():
		return error_resp(INVALID_CHOICE.format('schoolName'), 'INVALID_CHOICE')
	
	elif 'className' in restdict.keys():
		return error_resp(restdict['className'][0], 'INVALID_CHOICE')	
	
	elif 'grade' in restdict.keys():
		return error_resp(restdict['grade'][0], 'INVALID_CHOICE')

	elif 'collegeName' in restdict.keys():
		return error_resp(restdict['collegeName'][0], 'INVALID_CHOICE')

	elif 'field' in restdict.keys():
		return error_resp(restdict['field'][0], 'INVALID_CHOICE')
	
	elif 'currentStudent' in restdict.keys():
		return error_resp(restdict['currentStudent'][0], 'INVALID_CHOICE')
	
	elif 'college_add_error' in restdict.keys():
		return error_resp(restdict['college_add_error'][0], 'COLLEGE_ADD_ERROR')
	
	elif 'uni_add_error' in restdict.keys():
		return error_resp(restdict['uni_add_error'][0], 'UNIVERSITY_ADD_ERROR')

	elif 'registration_id' in restdict.keys():
		return error_resp(restdict['registration_id'][0], 'REGISTRATION_ID_EXIST')
	
	elif 'type' in restdict.keys():
		return error_resp(restdict['type'][0], 'TYPE_ERROR')
	
	elif 'non_field_errors' in restdict.keys():
		if restdict.get('non_field_errors')[0] == "User is already registered with this e-mail address.":
			return error_resp(EMAIL_IN_USE, 'EMAIL_IN_USE')
		elif restdict.get('non_field_errors')[0] == "Incorrect value":
			return error_resp(INVALID_TKN, 'INVALID_TKN')
		elif restdict.get('non_field_errors')[0].code == 'unique':
			return error_resp(restdict['non_field_errors'][0], 'UNIQUE_CODE_VIOLATION')
	
	return error_resp(restdict['non_field_errors'][0], '')


def success_resp(msg, err, restdict):	
	resp = {'message': msg, 'error': err, 'body': restdict}
	return resp


def error_resp(msg, err, restdict={}):
	resp = {'message': msg, 'error': err, 'body': restdict}
	return resp
