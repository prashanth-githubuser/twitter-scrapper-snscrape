import streamlit as st
import snscrape.modules.twitter as sntwitter 
import pandas as pd
import pymongo
import base64
from datetime import datetime
import time




def date_validation(start_date,end_date ):
    
    try:
        start_date= datetime.strptime(start_date,'%Y-%m-%d')
        end_date  = datetime.strptime(end_date ,'%Y-%m-%d')
    except :
        st.error("Please enter valid date format")




@st.cache_data
def scrapping(text:str,likes:str,end_date:str,start_date:str,limit):
    query = text+" "+"min_faves:"+str(likes)+" "+"until:"+end_date+" "+"since:"+start_date

            #"Machine Learning min_faves:100 until:2022-12-31 since:2022-12-01"
    tweets = []
    progress = st.progress(0)
    loaded_tweets = st.empty()
        
    count = int(0) 
    for tweet in sntwitter.TwitterSearchScraper(query).get_items():
        tweets.append([
                        tweet.date,
                        tweet.id,
                        tweet.url,
                        tweet.rawContent,
                        tweet.replyCount,
                        tweet.retweetCount,
                        tweet.lang,
                        tweet.sourceLabel,
                        tweet.hashtags,
                        tweet.likeCount
                        ])
        
        count = count+1
#--------------------------------------------Progress bar---------------------------
        loaded_tweets.text(f"Loaded Tweets:{count}/{limit}")
        progress_val = count/int(limit)

        if len(tweets) != limit and progress_val<1.0:
            time.sleep(0.01)                
            progress.progress(progress_val)
                                
            
            if len(tweets) == limit and progress_val<1.0:
                progress_val = 1.0
                time.sleep(0.01)                
                progress.progress(progress_val)
                st.success("Tweets Scrapped successfully")
                
            
            elif progress_val>1.0 and len(tweets) == limit :
                progress_val = 1.0
                time.sleep(0.01)
                progress.progress(progress_val)
                st.success("Tweets Scrapped successfully")
                
                       
        elif len(tweets) == limit:
            progress_val = 1.0
            time.sleep(0.01)                    
            progress.progress(1.0)
            st.success("Tweets Scrapped successfully")
            
            break

    return tweets, text, limit

@st.cache_data
def create_dataframe(tweets):
    df = pd.DataFrame(tweets,
                    columns = ["Date","ID","URL","Content","Reply_Count","Retweet_count","Lang","Source","Tag","Likes"]
                    )
    scrapped_data = str(df.shape[0])

    return df, scrapped_data

def database(tweet,limit,df):
    try:
        client = pymongo.MongoClient("mongodb+srv://user_0:root0000@cluster99.j3n8dnp.mongodb.net/?retryWrites=true&w=majority")
        db = client.twitter_scrapped_data
        time_stamp = datetime.today().strftime("%Y-%m-%d")
        collection_name = str(tweet+" "+str(limit)+" "+"tweets"+" "+time_stamp)
        collection_list = db.list_collection_names()
        
        if collection_name in collection_list:
            pass

        elif collection_name not in collection_list:
            collection = db[collection_name]
            #df.reset_index(inplace=True)
            collection.insert_many(df.to_dict("records"))
    except:
        st.error("Service Error")
    

@st.cache_data
def download_csv(data):

    b64 = base64.b64encode(data.to_csv().encode()).decode()
    file_name = "tweets.csv"
    href_csv = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">➥Click Here to download in CSV format!!</a>'
    return href_csv

@st.cache_data
def download_json(data):

    b64 = base64.b64encode(data.to_json().encode()).decode()
    file_name = "tweets.json"
    href_json = f'<a href="data:file/json;base64,{b64}" download="{file_name}">➥Click Here to download in JSON format!!</a>'
    return href_json


st.set_page_config(page_title = "Twitter Scrapper", layout = "wide")

#Header
st.title("Twitter Scrapping Project")



#sidebar

nav = st.sidebar.radio("Navigation Menu",["Home Page","Collect Data"])

#========================================================(Page-1)=============================================================
if nav == "Home Page":
    st.image("https://www.techtodayinfo.com/wp-content/uploads/2020/01/Web-Scraping.jpg", width = 800)
    st.write('''
                 # Description:
                 Data collection is the first step in the field of Data analytics, Machine learning and Data science. 
                 As edge and technologies evolve, 
                 more types of data are being collected from more data collection devices than ever before.
                 This web scrapping project will simplify and accelerate the process of collecting data from the twitter data using snscrape
                 python lib  and you can download the data in "CSV and JSON format".
                 To get the real facts on Twitter, You can collect the data like (date, id, url,
                 tweet content,reply count, retweet count,language, source, like count etc) from twitter.
                 ''')
    
    st.write('''### Sample Scrapped data''')
    
    sample_tweets = {"Date":["2023-01-01","2022-01-02","2023-01-03","2022-01-04","2022-01-05"],
                     "ID":["16432xxx","16165xxx","12431xxx","12431xxx","135312xxx"],
                     "URL":["https://twitter.com","https://twitter.com","https://twitter.com","https://twitter.com","https://twitter.com"],
                     "Content":["Hello Twitter","Hello Elon","Hello AI","Hello ML","Hello data"],
                     "Reply_Count":["24522","45263","3640","8765","8768"],
                     "Retweet_count":["2000","45263","8768","24522","3640"],
                     "Lang":["en","en","en","en","en"],
                     "Source":["Twitter for android","Twitter for xPhone","Twitter for flatter","Twitter for droidd","Twitter for android"],
                     "Tag":["Twitter","Spacex","AI","MLops","Data"],
                     "likes":["3524","7534","4985","6590","8970"]
                    }

    sample_df = pd.DataFrame(sample_tweets, index = [1,3,4,5,6])
    st.write(sample_df)
    
    st.write("Use side bar for Collecting the data from twitter")
    
    st.header('''Project source code''')
    st.write('''Do you want to know how this project is completed??? Check my Github repo, link given below and 
             give a star for my work if you liked it''',":star:")
    
    st.write("[Github Repositories](https://github.com/prashanth-githubuser)",":link:")

#=======================================================(Page-2)========================================================================   
if nav == "Collect Data":
    
    st.image("https://www.bridgingpointsmedia.com/wp-content/uploads/2020/07/webscrap1.jpg",
             caption='"No data is clean, but most is useful"~Dean Abbott',
             width = 800)
    
    with st.form(key = "form1"):
        
        st.header("Start Collecting the Twitter Data!!!!")
       
        text = st.text_input("*Search Tweets: (eg:- #Machine_learning or Machine learning)") #Text input
        
        col1,col2 = st.columns((1,1))
        
        with col1:
            
            start_date = st.text_input("Enter Start Date YYYY-MM-DD") #start_date input
       
        with col2:
        
            end_date = st.text_input("Enter End Date YYYY-MM-DD") #end_date input
    
        col3,col4 = st.columns((1,1))
        
        with col3:
            
             likes = st.number_input("Enter minimum likes (optional)",0, step = 100) #likes input
       
        with col4:
        
            limit = st.number_input("Enter the no of required tweets (Min:100)",100,step = 100)  #limit input
            
        download_option = st.selectbox("Select Format",["Select Format","CSV","JSON"])    
        form1_result = st.form_submit_button("Start Scrapping tweets")

        if text and start_date and end_date and form1_result:
            
            generated_tweets, text, limit= scrapping(text,likes,end_date,start_date,limit)

            st.write("No Progress?? Change the date range")

            df,scrapped_data = create_dataframe(generated_tweets)
            #db section
            database(text,limit,df)

            time.sleep(1.2)
            st.write("Sample Tweets")
            st.write(df.head())
            st.write("__Total Scrapped Data:__",scrapped_data)
#--------------------------------------------Download------------------------------------------ 
            if download_option == 'CSV':
                
                st.markdown(download_csv(df), unsafe_allow_html=True)
            elif download_option == 'JSON':
                st.markdown(download_json(df), unsafe_allow_html=True)

        elif form1_result and  start_date and end_date :
                #Date Validation
                date_validation(start_date,end_date)
                    
        elif form1_result:
                
            st.info(":blue[Please enter the fields]", icon="ℹ️")