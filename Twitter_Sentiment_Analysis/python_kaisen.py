import requests
import json

bearer_token = "AAAAAAAAAAAAAAAAAAAAANv1dAEAAAAA0HBGNjkDHJZp8zNioPIb1%2FO6h10%3DbX5txHhikmdcwtuWIyfzspjMy4EeQ8hdkw0Ich6cVITo5WzV8P"

def make_bearer_token(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    return r

def get_search_results(search_query, max_results=100, next_token=False):
    """
    Getting search results
    """
    url = "https://api.twitter.com/2/tweets/search/recent"
    query_params = {
        'query': search_query,
        'tweet.fields': 'id,text,created_at,lang,public_metrics,geo,author_id',
        'max_results': max_results
    }
    if next_token:
        query_params['next_token'] = next_token
    resp = requests.get(url, auth=make_bearer_token, params=query_params)
    
    if resp.status_code != 200:
        print (resp.text)
#         return next_token

    return resp.json()

def __get_user_details__(username):
    url = "https://api.twitter.com/2/users/by/username/"+username
    resp = requests.get(url, auth=make_bearer_token)
    if resp.status_code != 200:
        print ("Some error happened!")

    return resp.json()
    
def get_user_tweets(username, max_results=100, next_token=None):
    user = __get_user_details__(username)
    
    url = "https://api.twitter.com/2/users/{}/tweets".format(user['data']['id'])
    
    query_params = {
        'tweet.fields': 'id,text,created_at,lang,public_metrics,geo,author_id',
        'max_results': max_results
    }
    
    if next_token:
        query_params['next_token'] = next_token
    resp = requests.get(url, auth=make_bearer_token, params=query_params)
    if resp.status_code != 200:
        print ("Some error happened!")

    return resp.json()



twts = get_user_tweets('elonmusk')
from tqdm import tqdm
tweets = []
r = get_search_results("#aap", 100)
tweets.append(r)

next_token = r['meta']['next_token']
for _ in tqdm(range(10)):
    r = get_search_results("#aap", 100, next_token)
    tweets.append(r)
    next_token = r['meta']['next_token']
import time
def get_1000_tweets(search_query):
    tweets = []
    r = get_search_results(search_query, 100)
    tweets.append(r)

    next_token = r['meta'].get('next_token')
    for _ in tqdm(range(10)):
#         time.sleep(1)
        r = get_search_results(search_query, 100, next_token)
        tweets.append(r)
        next_token = r['meta'].get('next_token')
    return tweets
# processing tweets
data = []                  # data is a list which contains dictionaries with attributes such as id, public_metrices, like_count etc. for different tweets.
for t in tqdm(range(len(tweets))):  
    data.extend(tweets[t]['data'])
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
nlp = spacy.load('en_core_web_sm')       # en_core_web_sm is a mode used by spaCy for webtexts.
nlp.add_pipe('spacytextblob')
# filtering out only english tweets

def calculate_sentiments(text):    
    '''text is the argument passed and it is passed throuh nlp to calculate sentiments.'''
    doc = nlp(text)   # doc contains the text that is passes through NLP.
    sent = {
        "sentiment": doc._.blob.polarity,       # polarity
        "subjective": doc._.blob.subjectivity   # depends upon personal opinions and judgements.
    }
    return sent    # so inside the processed text sentiment and subjectivity is seen is calculated.
    
data = [d for d in data if d['lang']=='en']     # filtering the tweets to english parts.
for d in data:
    d['sentiment'] = calculate_sentiments(d['text'])     # appeding a new key in data which includes
def extract_hour(t):
    '''It gives us the hour when the person writes the tweet.'''
    return t.split('T')[-1].split(':')[0]

for d in data:
    d['hour'] = extract_hour(d['created_at'])    # appending a new key called hour which gives us the hour where the tweet has been written.
#now every tweet (d) in data -->contains an additional key called hour.
from collections import defaultdict

# def __dict__(v):
    
hourly_sentiments = defaultdict(int)             # for each hour sentiments and subjectivity is set default using default dictionary.
hourly_subjectivity = defaultdict(int)
N = len(data)                      # Total length of the data is defined.
for d in data:
    h = int(d['hour'])             # now we are iterating over that hour value created above.
#     if hourh:
    hourly_sentiments[h] += d['sentiment']['sentiment']    #analising total hourly sentiment calculation for that hour.
    hourly_subjectivity[h] += d['sentiment']['subjective'] #analising total hourly subjectivity calculation for that hour
def normalize(_dict):
    v = _dict.values()    # v has all the values corresponding to hour key.
    #print(v)
    _min = min(v)         # max and min is calculated
    _max = max(v)
    for k in _dict:
        if(_max-_min==0):
            _dict[k]=1
        else:
            _dict[k] = (_dict[k] - _min)/(_max - _min)   # normalizing the values. Here it scales upto all the values between 0 to 1.
    return _dict

hourly_sentiments = normalize(hourly_sentiments)
hourly_subjectivity = normalize(hourly_subjectivity)
import matplotlib.pyplot as plt
x_sent = list(hourly_sentiments.keys())
y_sent = list(hourly_sentiments.values())
x_sub = list(hourly_subjectivity.keys())
y_sub = list(hourly_subjectivity.values())
# upside bar graphs
plt.figure(figsize=(20,10))
plt.bar(x_sent,y_sent, label="Sentiments")
plt.bar(x_sub, y_sub, label="Subjectivity")
plt.xlabel(" <---- Hour of the day ----> ")
plt.ylabel("Sentiment")
plt.title("Sentiment and Subjectivity values hourly for last 1000 tweets")
plt.legend()
plt.xticks(x_sent)
plt.show()
# create a document containing all tweets
text = ''            # it contains all the text of the tweet.
for twt in data:     # twt is one single tweet in all the data and it has key ['text'] associated which contains text associated with it.
    text += twt['text']   # collective tweet texts are appended in text
    text+='\n'
find='#'              # this is a code where the starting point is set as # to find the hashtags.
end=' '               # The ending point is set as " " i.e space.
hashtags=[]           # It is a list that contains all the hastags found.
length=len(text)
for i in tqdm(range(length)):   # iterating over text i.e all the text.
    if(find==text[i]):          # i is index.
        j=i                     # storing j as i to and j is used to see where the string ends and j=i means refrence is set and now length of hastag is 0 but while loop results in giving us the end of that particular hashtag.
        while(text[j]!=end ):    # Finding j until the hastag ends i.e where is the space.
            j=j+1     
            if(j==len(text)):
                break
            # j is index.
            #print(text[j])
            #print("Value of j is",j," and value of i is",i)
        hashtags.append(text[i+1:j])

#ck_sort
def quick_sort(lst):
	#to sort the list using quick sort we will use recursion 
	if len(lst)<=1:
		return lst
	#setting if condition for base case which will return list if it has only one element 	
	ele=lst[len(lst)-1]
	#setting last element of list to a variable 'ele'
	#defining two empty lists lst1 and lst2
	lst1=[]
	lst2=[]
	for i in range(len(lst)-1):
		if lst[i]<ele:
			lst1.append(lst[i])
	#elements smaller than ele will be stored in lst1		
		else:
			lst2.append(lst[i])
	#elements bigger than ele will be stored in lst2		
	sorted_lst1=quick_sort(lst1)
	#calling quick_sort fucntion of lst1 and lst2 (using recursion)
	sorted_lst2=quick_sort(lst2)
	x = sorted_lst1+[ele]+sorted_lst2
	#combining the sorted lists and the element ele 
	return x

import collections
hashes_lowercase=[]
for j in hashtags:
    hashes_lowercase.append(j.lower())   # amking all the hashtags in lowercase alphabets.
quick_sort(hashes_lowercase)    # just sorting hashes.

hashtags = set(hashes_lowercase)    # hashtag list is set to a new list with the same hashtags but in lowercase.

lower_data = []    # earlier we lowercased the hashtags only but now we will lowercase all the data.
for d in data:
    _d = d.copy()                         # only the text key is changed rest all is copied.
    _d['text'] = d['text'].lower()        # d['text'] contains the text of a single tweet.
    lower_data.append(_d)                 # Appending the new dictionary with changed value of key called text in new list called lower_data.

hashtags_sentiment = defaultdict(int)
# optimize this
for h in tqdm(hashtags):
    _h = '#'+h             # _h is the new string of lowercase hastags but now with a hash sign.
    for twt in lower_data: # Searching the lowercased hastag in lower_data. 
        if _h in twt['text']: # if found then the tweet contains that particular text.
            hashtags_sentiment[h] += twt['sentiment']['sentiment']   # sentiment of that tweet is calculated if the hashtag is found in a tweet.

hashtags_sentiment = normalize(hashtags_sentiment)              # making the value betyween 0 to 1.
# hashtags_sentiment is a dictionary that conatins sentiment of the tweets of a particular hashtag. The key is hashtag and the value
hash_tuple = [(h, hashtags_sentiment[h]) for h in hashtags_sentiment]
#hash_tuple is the list containing tuple corresponding to that particular dictionary.
#hash_tuple

hash_tuple = sorted(hash_tuple, key=lambda x: x[1])    # sorting of that particular tuple's list.

p_h = hash_tuple[-10:]
n_h = hash_tuple[:10]
# find the median or neutral sentiment values.
length_hatu=int(len(hash_tuple)/2)
m_p = hash_tuple[length_hatu-5:length_hatu+4]    # finding the median sentiments.
print("Top 10 positive along with their sentiments: ",p_h)
print("Top 10 negative along with their sentiments: ",n_h)
print("Top 10 neutral along with their sentiments: ",m_p)

has=(collections.Counter(quick_sort(hashes_lowercase)))   # has is a dictionary which stores the frequency corresponsing to each hashtag
has=[(h,has[h])for h in has]    # now has is converted to a tuple(x,y) such that x = key and y = value.

top_frequent_tweets = sorted(has, key=lambda x: x[1])     # top_frequent_tweets include the list of tuples which is sorted by value.

top10=[]    # top10 is a list which contains the list of top 10 most tweeted tweets.
for tweets in tqdm(range(10)):
    top10.append(top_frequent_tweets[len(top_frequent_tweets)-1-tweets])
top10
for i in top10:
    if '\n' in i[0]:
        top10.remove(i)


def clean(string):
    return ''.join([i for i in string if i.isalpha()])

top10 = [(clean(t[0]), t[1]) for t in top10 ]

data_of_top_10_tweets=[]
top_results=[]
i=0
token = None
for tops in tqdm(top10):  # searching for top10 value that is we are just searching for hashtags
    r = get_1000_tweets('#'+tops[0])
    data_of_top_10_tweets.append(r)            # whole data is taken for top 10 frequent hashtag under that hashtag.


data_top10_data = []        # data_top10_data is a list which contains dictionaries with attributes such as id, public_metrices, like_count etc. for different tweets.
for j in range(len(data_of_top_10_tweets)):
    for t in tqdm(range(len(data_of_top_10_tweets[j]))): 
        print(data_of_top_10_tweets[j][t].get('data'))
        count=0
        #print(type(data_of_top_10_tweets[t].get('data')))
        #data_of_top_10_tweets[t]['data'].append({'text' : '\n'})
        for f in tqdm(range(len(data_of_top_10_tweets[j][t].get('data')))):
            print(data_of_top_10_tweets[j][t]['data'][count])
            if '\n' in data_of_top_10_tweets[j][t]['data'][count]['text']:
                data_of_top_10_tweets[j][t]['data'].remove(data_of_top_10_tweets[j][t]['data'][count])
                count=count-1
            count=count+1
        data_top10_data.extend(data_of_top_10_tweets[j][t].get('data'))



data_top10_data = [d for d in data_top10_data if d['lang']=='en']# filtering the tweets to english parts.
# print(data_top10_data)
for d in data_top10_data:
    d['text']=d['text'].lower()
    print(d['text'])
for d in tqdm(data_top10_data):
    d['sentiment'] = calculate_sentiments(d['text'])     # appeding a new key in data which includes the tweet's sentiments.


j={'sentiment':0}
for t in tqdm(data_top10_data):
    j['sentiment'] =j['sentiment'] +t['sentiment']['sentiment']
ans_senti=j['sentiment']



final_answer = ans_senti /len(data_top10_data)
print("This is the total sentiment/number of tweets: ",final_answer)
#here we can compare the final answer directly.

