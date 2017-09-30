import os

if 'OPENSHIFT_APP_NAME' in os.environ.keys():
    UPLOAD_FOLDER = os.path.join(os.environ['OPENSHIFT_TMP_DIR'],'upload')
    OUTPUT_FOLDER = os.path.join(os.environ['OPENSHIFT_TMP_DIR'],'output')
else:
    UPLOAD_FOLDER = os.path.join(os.getcwd(),'temp','upload')
    OUTPUT_FOLDER = os.path.join(os.getcwd(),'temp','output')

MAX_CONTENT_LENGTH = 3 * 1024 * 1024
MAX_FILE_CONTENT_LENGTH = 1 * 1024 * 1024
MAX_WEB_CONTENT_LENGTH = 1 * 1024 * 1024
ALLOWED_EXTENSIONS_TXT = ['txt']
ALLOWED_EXTENSIONS_IMG = ['png', 'jpg', 'jpeg']