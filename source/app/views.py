import os
from flask import render_template, request, send_from_directory, redirect
from threading import Thread
from app import app
from app import twitapp,tagcloud
from app.utils import maintenance,gettoken,process_source,process_uploaded_txt_file,allowed_file_img

@app.route('/',methods=['GET'])
def index():
    maintenance()
    if bool(request.args):
        return redirect('/')
    else:
        return render_template('index.html')


@app.route('/',methods=['POST'])
def index_process():
    if 'token' in request.form.keys():
        return recolor_tagcloud(request=request)
    else:
        return create_tagcloud(request=request)


@app.route('/updatetwitter',methods=['GET'])
def update_twitter_tagclouds():
    t = Thread(target=twitapp.post_tags_from_url,args=('news.yandex.ru',))
    t.start()
    return render_template('redirect.html')
    #return redirect('/')


def create_tagcloud(request):
    token = gettoken()

    #SOURCEFILE AND URL
    try:
        sourcefilename = process_source(token=token,uploadedfile=request.files['source'],weburl=request.form['pageurl'])
    except:
        return render_template('index.html', error='nosource')

    #STOPWORDSFILE
    if request.files['stopwords']:
        try:
            stopwordsfilename = os.path.join(app.config['UPLOAD_FOLDER'], ''.join(['stopwords', token, '.txt']))
            process_uploaded_txt_file(uploadedfile=request.files['stopwords'], targetfilename=stopwordsfilename)
        except:
            return render_template('index.html', error='stoptxtfile')
    else:
        stopwordsfilename = None

    #MASKFILE
    file = request.files['mask']
    if file:
        if allowed_file_img(file.filename) and file.content_length < app.config['MAX_FILE_CONTENT_LENGTH']:
            maskfilename = os.path.join(app.config['UPLOAD_FOLDER'], ''.join(['maskfile', token]))
            request.files['mask'].save(maskfilename)
        else:
            return render_template('index.html', error='maskfile')
    else:
        maskfilename = None

    #MAX_COUNT
    if request.form['max_words']:
        max_words = int(request.form['max_words'])
    else:
        max_words = 250


    randomizecolors = True if 'randomizecolors' in request.form.keys() else False
    ignorebasestopwords = True if 'ignorebasestopwords' in request.form.keys() else False
    outputfilename = os.path.join(app.config['OUTPUT_FOLDER'], ''.join(['tagcloud_', token, '.png']))
    layoutfilename = os.path.join(app.config['UPLOAD_FOLDER'], ''.join(['layout', token]))

    if tagcloud.createcloud(sourcefilename=sourcefilename,
                            stopwordsfilename=stopwordsfilename,
                            ignorebasestopwords=ignorebasestopwords,
                            outputfilename=outputfilename,
                            layoutfilename=layoutfilename,
                            maskfilename=maskfilename,
                            randomizecolors=randomizecolors,
                            max_words=max_words):
        return render_template('result.html',
                               filename=''.join(['/output/',''.join(['tagcloud_', token, '.png']),'?',gettoken()]),
                               randomizecolors=randomizecolors,
                               token=token)
    else:
        return render_template('index.html', error='tagcloud')


def recolor_tagcloud(request):
    token = request.form['token']

    randomizecolors = True if request.form['randomizecolors'] == 'True' else False

    maskfilename = os.path.join(app.config['UPLOAD_FOLDER'], ''.join(['maskfile', token]))
    if not os.path.isfile(maskfilename):
        maskfilename = None

    outputfilename = os.path.join(app.config['OUTPUT_FOLDER'], ''.join(['tagcloud_', token, '.png']))

    if tagcloud.recolor_cloud(outputfilename=outputfilename,
                             maskfilename=maskfilename,
                             randomizecolors=randomizecolors,
                             token=token):
        return render_template('result.html',
                               filename=''.join(['/output/', ''.join(['tagcloud_', token, '.png']), '?', gettoken()]),
                               randomizecolors=randomizecolors,
                               token=token)
    else:
        return render_template('index.html', error='error')


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/examples')
def see_examples():
    return render_template('examples.html')


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(os.path.abspath(app.config['OUTPUT_FOLDER']),filename)

