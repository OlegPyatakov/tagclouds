#!/usr/bin/python3

import os, re, random, ast
import pymorphy2
from wordcloud import WordCloud, ImageColorGenerator
from app import app
from PIL import Image
from numpy import array

def createcloud(sourcefilename,layoutfilename,outputfilename,stopwordsfilename=None,ignorebasestopwords=None,maskfilename=None,randomizecolors=None,max_words=250):

    try:
        tags = get_tags_from_filename(sourcefilename=sourcefilename)
    except:
        return None

    try:
        stopwords = get_stopwords(stopwordsfilename=stopwordsfilename,ignorebasestopwords=ignorebasestopwords)
    except:
        return None


    mask = get_mask(maskfilename=maskfilename)
    if maskfilename:
        image_colors = ImageColorGenerator(mask)
    else:
        image_colors = get_base_color_func()


    if randomizecolors: image_colors = random_color_func



    wordcloud = get_wordcloud(stopwords=stopwords,
                              mask=mask,
                              color_func=image_colors,
                              max_words=max_words)

    wordcloud.generate(tags)

    with open(layoutfilename,'w',encoding='UTF-8') as f:
        f.write(str(wordcloud.layout_))

    wordcloud.to_file(outputfilename)

    return True


def recolor_cloud(token,outputfilename,maskfilename=None,randomizecolors=None,):

    if randomizecolors:
        image_colors = random_color_func
    else:
        image_colors = get_base_color_func()

    if maskfilename:
        mask = array(Image.open(maskfilename))
    else:
        mask = None

    wordcloud = get_wordcloud(mask=mask,
                              color_func=image_colors)

    layoutfilename = os.path.join(app.config['UPLOAD_FOLDER'], ''.join(['layout', token]))
    with open(layoutfilename, 'r',encoding='UTF-8') as f:
        wordcloud.layout_ = list(ast.literal_eval(f.read()))

    wordcloud.recolor(color_func=image_colors)
    wordcloud.to_file(outputfilename)
    return True


def get_wordcloud(stopwords=None,mask=None,color_func=None,height=1080,width=1920,max_words=250):
    if color_func==None: color_func=get_base_color_func()
    wordcloud = WordCloud(background_color='white',
                          stopwords=stopwords,
                          font_path=os.path.dirname(os.path.abspath(__file__)) + '/arialbd.ttf',
                          height=height,
                          width=width,
                          max_words=max_words,
                          prefer_horizontal=0.7,
                          mask=mask,
                          color_func=color_func)
    return wordcloud


def get_tags_from_filename(sourcefilename):

    morph = pymorphy2.MorphAnalyzer()
    tags = ''
    with open(sourcefilename, encoding='UTF-8') as f:
        for word in f.read().split():
            valids = re.sub(r"[^A-Za-zА-Яа-я]+", '', word)
            tags = tags + morph.parse(valids)[0].normal_form + '\n'

    return tags


def get_stopwords(stopwordsfilename,ignorebasestopwords=None):

    if ignorebasestopwords:
        stopwords = ''
    else:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/basestopwords.txt', 'r', encoding='utf-8') as f:
            stopwords = f.read()

    if stopwordsfilename:
        with open(stopwordsfilename, encoding='UTF-8') as f:
            stopwords = f.read()

    return stopwords


def get_mask(maskfilename):
    if maskfilename:
        resizeimage(maskfilename)
        mask = array(Image.open(maskfilename))#imread(''.join([maskfilename,'.png']))
    else:
        mask = None
    return mask


def get_base_color_func():
    hue = random.randint(0,360)
    def base_color_func(word=None, font_size=None, position=None, orientation=None, random_state=None, **kwargs):
        return 'hsl(%d, 100%%, %d%%)' % (hue, int(72/256*random.randint(70,130)))
    return base_color_func
    #return 'hsl(%d, 100%%, %d%%)' % (int(209), int(72/256*random.randint(70,130)))


def resizeimage(imagefilename):
    image = Image.open(imagefilename)
    resizeratio = min(1920 / image.size[0], 1080 / image.size[1])
    image.resize((int(image.size[0] * resizeratio), int(image.size[1] * resizeratio)), Image.ANTIALIAS).save(''.join([imagefilename, '.png']))
    return True


def random_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return 'hsl(%d, 100%%, %d%%)' % (random.randint(1,360), int(72/256*random.randint(70,130)))


