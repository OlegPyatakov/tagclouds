import os,datetime,hashlib
from app import app,webscrape
import chardet

def process_source(token,uploadedfile=None,weburl=None):
    sourcefilename = os.path.join(app.config['UPLOAD_FOLDER'],''.join(['source',token,'.txt']))

    if uploadedfile:
        process_uploaded_txt_file(uploadedfile=uploadedfile,targetfilename=sourcefilename)


    if weburl:
        text = webscrape.gettextfromurl(weburl)
        if text and len(text) < app.config['MAX_WEB_CONTENT_LENGTH']:
            with open(sourcefilename, "a", encoding='utf-8') as f:
                f.write(text)

    if os.stat(sourcefilename).st_size:
        return sourcefilename
    else:
        return None


def process_uploaded_txt_file(uploadedfile,targetfilename):
    if allowed_file_txt(uploadedfile.filename) and uploadedfile.content_length < app.config['MAX_FILE_CONTENT_LENGTH']:
        uploadedfile.save(targetfilename)
        with open(targetfilename, "r", encoding=getencoding(targetfilename)) as f:
            text = f.read()
        with open(targetfilename, "w", encoding='utf-8') as f:
            f.write(text)
    return True


def allowed_file_txt(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS_TXT']


def getencoding(filename):
    with open(filename, 'rb') as f:
        rawdata = f.read()

    if chardet.detect(rawdata)['encoding']:
        return chardet.detect(rawdata)['encoding']
    else:
        return 'UTF-8'


def gettoken():
    return str(hashlib.sha1(str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')).encode('utf-8')).hexdigest())


def allowed_file_img(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS_IMG']


def maintenance():
    checkfolder(app.config['UPLOAD_FOLDER'])
    checkfolder(app.config['OUTPUT_FOLDER'])
    return True


def checkfolder(folderpath=None):
    if os.path.isdir(folderpath):
        cutoff = datetime.datetime.now()-datetime.timedelta(minutes=10)
        for file in os.listdir(folderpath):
            if datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(folderpath,file))) < cutoff:
                os.remove(os.path.join(folderpath,file))
    else:
        os.makedirs(folderpath)
    return True
