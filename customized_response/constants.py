import pytz
from datetime import date
from rest_framework import status


UTC = pytz.utc
BD_TIME = pytz.timezone('Asia/Dhaka')
BASE_URL = 'https://www.examsspace.com'
BACKEND_BASE_URL = 'https://exms-302404.et.r.appspot.com/api/'
BACKEND_DEV_BASE_URL = 'http://34.126.123.64:8000'
ACS_TKN_DUR = 2   #In Hours
REF_TKN_DUR = 100  #In Days
PASS_MIN_LEN = 8
PASS_MAX_LEN = 65
EMAIL_MIN_LEN = 11
EMAIL_MAX_LEN = 255
VIEW_HISTORY_THRESHOLD = 65
START_DATE = date(2021, 2, 7)
BD_PHONE_NUM = '^(\+88)(01[3-9]\d{8})' #'^(\+88|88)?(01[3-9]\d{8})' 


#Error Messages
NULL = 'NULL'
EMPTY_TKN = 'The token is empty'
INVALID_TKN = 'The token is invalid'
EXPIRED_TKN = 'The token has expired'
WRONG_PASS = 'Wrong password'
USR_NOT_FOUND = 'No user is found with provided credentials'
PASS_SHORT = 'Use 8 characters or more for your password'
PASS_NOT_MATCH = 'Password did not match'
EMAIL_IN_USE = 'Email already exists'
USR_PASS_INCORRECT = 'Incorrect username or password'
ACC_NOT_FOUND = 'No account is found with this email'
USR_EXIST = 'A user with that username already exists'
PERMISSION_DENIED = 'You do not have permission to perform this action'
AUTH_CRE_NOT_FOUND = 'Authentication credentials were not provided'
PROFILE_NOT_FOUND = 'No profile found for the user' 
WWW_AUTH = 'Provide username and password to login'
INVALID_REQ = 'Your request is invalid'
EXAM_NOT_ALLOWED = 'You can retake the exam only once if you fail'
RESULT_ADD_ERROR = 'Results has already been added'
PACK_ENROLLED_PREV = 'Package already enrolled'
PROFILE_EXIST = 'A profile with that username already exists'
INVALID_FIRST = 'Use 2 characters or more for your first name'
INVALID_LAST = 'Use 2 characters or more for your last name'
EMPTY_FIELD = 'You can not leave {} field empty'
DATE_FORMAT_ERROR = 'Please give the date in DD-MM-YYYY format'
CITY_NOT_SELECT = 'You must select a city'
NO_EXAM_AVAILABLE_IN_PACKAGE = 'There are no exams available in this package'
VIEW_HISTORY_THRESHOLD_EXCEEDED = 'Total marks in this exam is beyond threshold'
CONTEST_ENROLLED_PREV = 'User has already enrolled in the competition'
ENROLL_TIME_UP = 'Enrollment time is over'
NOT_ENROLLED = 'User is not enrolled'
DATA_SUBMIT_PREV = 'User has already submitted the data'
DATA_NOT_FOUND = 'User has not submitted any data yet'
REQ_USER_IS_NOT_ADMIN = 'Requested user is not admin'
PACK_BULK_IMPORT_FAIL = 'Package import has failed'
EXAM_BULK_IMPORT_FAIL = 'Exam import has failed'
QUES_BULK_IMPORT_FAIL = 'Question import has failed'
WRONG_FILE_EXT = 'This is not a xlsx file'
INVALID_DATE = 'The Given Date is invalid'
EXAM_NOT_FOUND = 'User did not participate in this exam'
TIME_UP = 'Time to submit / update data is over'
IMAGE_NOT_FOUND = 'No image found with given URL for the User'
INVALID_MOBILE_NUM = 'Enter a valid phone number. Add corresponding country code(e.g. +8801712345678 for Bangladesh or +12125552368 for USA)'
INVALID_EMAIL = 'This is an invalid email address'
MOBILE_NUM_EXISTS = 'This mobile number already exists'
DELETE_ERROR = 'You can not delete your primary contact information'
INVALID_FATHER_INFO = 'Father information is invalid'
INVALID_MOTHER_INFO = 'Mother information is invalid'
INVALID_SPOUSE_INFO = 'Spouse information is invalid'
INVALID_CHOICE = 'Invalid choice for {} field'
ADDRESS_NOT_FOUND = 'No address found for the user'
INVALID_EDUCATION_INFO = 'Education information is invalid'
UNAUTHORIZED_ACCESS = 'User is not authorized for this action'
INVALID_INFO = 'Information is invalid'
NOT_FOUND = 'Data Not Found'
IMAGE_SIZE_ERROR = 'Image size can not exceed 5 MB'
DATE_ERROR = 'Start date / end date can not be in between other institutions\' start date and end date'
END_DATE_BOUND_ERROR = 'End date can not be ahead of start date'
CLASS_ERROR = 'User can not be in the same class for two different schools or colleges'
CLASS_BOUND_ERROR = 'This school does not have this class'
COLLEGE_ADD_ERROR = 'Current school students can not add college'
FIELD_UPDATE_ERROR = 'Class 10 / 12 students can not change their field'
FIELD_ERROR = 'Commerce students can not take science and arts students can not take science / commerce'
FIELD_BOUND_ERROR = 'This college does not have this field'
CURRENT_STUDENT_ERROR = 'End date suggests that user is not a current student'
UNI_ADD_ERROR = 'Current school / college students can not add university'
WRONG_DATA_FORMAT = 'There are errors in the excel sheet'
WRONG_SHEET_NAME = 'Incorrect primary sheet name'
DEVICE_REG_ID_EXIST = 'Registration id for this device already exists'



#Success Messages
USR_CREATE_SUCCESS = 'User is created successfully'
LOG_IN_SUCCESS = 'User has logged in successfully'
PROFILE_CREATE_SUCCESS = 'Profile is created successfully'
PROFILE_UPDATE_SUCCESS = 'Profile is updated successfully'
USR_FOUND = 'User information is retrieved successfully'
PASS_CHANGE_SUCCSS = 'Password has been changed successfully'
ACS_TKN_GET = 'Access token is retrieved successfully'
ACC_ACTIVATE_SUCCESS = 'Your account has been activated successfully'
LOG_OUT = 'User has logged out successfully'
ACC_FOUND = 'An account is found with this email'
PASS_RESET_SUCCSS = 'Password has been reset successfully'
FETCH_SUCCESS = 'Requested view is fetched successfully'
PACK_ENROLLED = 'User has enrolled the package successfully'
PACK_PIN = 'Package has been pinned successfully'
PACK_UNPIN = 'Package has been unpinned successfully' 
RESULT_ADDED = 'Result has been added successfully'
CONTEST_ENROLL = 'User has enrolled the contest successfully'
DATA_SUBMIT_SUCCESS = 'User has submitted the data successfully'
DATA_UPDATE_SUCCESS = 'User has updated the data successfully'
RESOURCE_DEL_SUCCESS = 'Resource has been deleted successfully'
ADD_NEWS_SUCCESS = 'News added successfully'
BULK_IMPORT_SUCCESS = 'Package, Exam and Questions have been imported successfully'
MOBILE_NUM_ADD_SUCCESS = 'Mobile number has been added successfully'  
MOBILE_NUM_UPDATE_SUCCESS = 'Mobile number has been updated successfully'
EMAIL_ADD_SUCCESS = 'Email has been added successfully'
EMAIL_UPDATE_SUCCESS = 'Email has been updated successfully'
GUARDIAN_INFO_ADD_SUCCESS = 'Guardian Information has been added successfully'
GUARDIAN_INFO_UPDATE_SUCCESS = 'Guardian Information has been updated successfully'
ADDRESS_UPDATE_SUCCESS = 'Address has been updated successfully'
UPDATE_SUCCESS = 'Information has been updated successfully'
DELETE_SUCCESS = 'Information has been deleted successfully'
DATA_ADD_SUCCESS = 'Data has been added successfully'
NOTIFICATION_SENT_SUCCESS = 'Notification has been sent successfully'



#Other String Literals
WELCOME_MSG = 'Welcome to ExamSpace!'
ACC_ACTIVATE_LINK = 'Please click on the link to activate your account:\n' + BASE_URL + '/activate?verify='
ACC_ACTIVATE_REDIRECT_LINK = BASE_URL
PASS_RESET_MSG = 'Request For Password Reset'
PASS_RESET_LINK = 'Please click on the link to reset your password:\n' + BASE_URL + '/reset-password?verify='



#Status Codes
CODE200 = status.HTTP_200_OK
CODE201 = status.HTTP_201_CREATED
CODE204 = status.HTTP_204_NO_CONTENT
CODE400 = status.HTTP_400_BAD_REQUEST
CODE401 = status.HTTP_401_UNAUTHORIZED
CODE403 = status.HTTP_403_FORBIDDEN
CODE404 = status.HTTP_404_NOT_FOUND



#Respose Headers
RESP_HEADERS = {'Access-Control-Allow-Origin' : '*'}