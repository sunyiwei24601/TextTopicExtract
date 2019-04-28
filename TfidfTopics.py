import json
import jieba
import gensim
from gensim import corpora,models
import time


#首先设置结巴分词的停用词
def get_stop_words():
    stopwords = [line.strip() for line in open('中文停用词库.txt', encoding='gbk').readlines()]
    stopwords += [' ', '-', '', '「', '」', '\r\n', "日", "月", "中"]
    return stopwords


#然后构建分词函数,这里是精确分词,对于文章的标题采用3倍的权重
def cut_words(sentence, title, stopwords):
    words = jieba.cut(sentence, cut_all=False)
    title_words = jieba.cut(title, cut_all=False)
    result_words = []
    for i in words:
        if i not in stopwords:
            result_words.append(i)
    for i in title_words:
        if i not in stopwords:
            for j in range(3):
                result_words.append(i)

    return result_words


#集合一年的新闻,生成背景语料库
def join_texts(docs, titles):
    texts = []
    stop_words = get_stop_words()
    for i  in range(len(docs)):
        text = cut_words(docs[i], titles[i], stop_words)
        texts.append(text)
    return texts


def get_key_words(sentence, tfidf):
    keywords_vector = tfidf[sentence]
    return keywords_vector

    
#展示前n个关键词
def show_top_key(keywords_vector, dictionary, n):
    s = sorted(keywords_vector, reverse=True, key = lambda x:x[1])
    return [(dictionary[i[0]], i[1]) for i in s[:n]]
    

def search_target_dailies(start_date, end_date, dailies):
    start_time = time.mktime(time.strptime(start_date, "%Y-%m-%d"))
    end_time = time.mktime(time.strptime(end_date, "%Y-%m-%d"))
    result_index = []
    for i in range(len(dailies)):
        daily = dailies[i]
        news_time = time.mktime(time.strptime(daily['node']['created_at'], "%Y-%m-%d"))
        if news_time <= end_time and news_time >= start_time:
            # print(news_time, daily['node']['created_at'])
            result_index.append(i)
    return result_index
    
    
if __name__ == "__main__":
    dailies = json.load(open('dailies.json'))
    #分别取得文本和标题,分为两部分,并用jieba分词转化为词向量
    docs = [i['node']['content'] for i in dailies]
    titles = [i['node']['title'] for i in dailies]
    texts = join_texts(docs, titles)
    #构建词向量字典,以及tfidf的计算模型并保存
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus)
    tfidf.save("./model.tfidf")
    
    words_vectors = []  #用以存储计算出来的tfidf值
    show_off_key_words = [] #用以存储最后的展示结果
    
    #获取满足指定日期内的新闻的编号和内容
    target_texts_index = search_target_dailies("2019-2-20", "2019-2-27", dailies)
    
    #对于目标项目,获取其指定的前n关键词主题,以及title和内容
    for i in target_texts_index:
        text = corpus[i]
        keywords = get_key_words(text, tfidf)
        words_vectors.append(keywords)
        show_off_key_words.append([dailies[i]['node']['title'],
                                   dailies[i]['node']['content'],
                                   show_top_key(keywords, dictionary, 10)])
    json.dump(show_off_key_words, open("article_topics.json"))
    
    #总结这段时间内的热点内容
    total_tfidf = {}
    for vector in words_vectors:
        for key, value in vector:
            if key in total_tfidf:
                total_tfidf[key] += value
            else:
                total_tfidf[key] = value
    week_topic_words = show_top_key(total_tfidf.items(), dictionary, 10)
    json.dump(week_topic_words, open('week_topic_words.json', "w"))