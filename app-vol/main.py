import uvicorn
from fastapi import FastAPI
import os 
from facebook_scraper import get_posts
import pandas as pd
import pyodbc
import sqlalchemy as sa
from sqlalchemy import create_engine,Table, Column, Integer, String, MetaData,insert
from urllib.parse import quote_plus
from mechanize import Browser
app = FastAPI()
#preparing database connection
port = 1443
driver = '{ODBC Driver 17 for SQL Server}'
Driver="{ODBC Driver 17 for SQL Server}";Server="tcp:elyadatascraping.database.windows.net,1433";Database="elyadata";Uid="bghoul";Pwd="boyzgo1919A@";Encrypt="yes";TrustServerCertificate="no";Connection_Timeout=30;
odbc_str ='DRIVER='+Driver+';SERVER='+Server+';PORT='+str(port)+';DATABASE='+Database+';UID='+Uid+';PWD='+Pwd
connect_str = 'mssql+pyodbc:///?odbc_connect='+quote_plus(odbc_str)
engine = create_engine(connect_str )
print(":connecting to DB")
connection = engine.connect()
metadata = sa.MetaData(bind=engine)
metadata.reflect(bind=engine)
print(":got MD")

async def getcookies():
    br = Browser()
    user='testapielyadata@gmail.com'
    passwd = "elyadataTESTAPI2022"
    br.set_handle_robots(False)
    ur="https://m.facebook.com"
    br.open(ur)
    br._factory.is_html = True
    br.forms()[0]['email']=user
    br.forms()[0]['pass']=passwd
    br.select_form(nr=0)
    br.submit()
    br.open(ur)
    res = br._ua_handlers['_cookies'].cookiejar
    return res

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/getposts/{keyword}/{np}")
async def scrape_posts(keyword,np):
    # try:

    post_df_full = pd.DataFrame()
    #getting raw data and storing it in dataframe
    res = await getcookies()
    print(res)
    n=int(np)
    for post in get_posts('bbcnews',cookies="cookies(4).json", pages=n):
        fb_post_df = pd.DataFrame.from_dict(post,orient="index")
        fb_post_df = fb_post_df.transpose()
        post_df_full = post_df_full.append(fb_post_df)
    l = ['post_id','text','post_text','shared_text','time','timestamp','image_lowquality','likes','comments','shares','post_url','user_id','username','user_url','is_live','available','reaction_count','page_id','was_live']
    df = post_df_full[l]
    df.to_sql('rawdata3',engine,index=False,if_exists="replace",schema="dbo")
    return {"message":"successfully scraped facebook and save to azure database"}
    # except Exception as e :
    #     return {"eroor" : e}
@app.get("/getprofiles/{keyword}")
async def scrape_profiles(keyword):
    profile = get_profile(keyword,cookies="cookies(4).json")
    # df.to_sql('rawdata3',engine,index=False,if_exists="replace",schema="dbo")

    return {"profile":profile}

@app.get("/getpostsdatabase/{np}")
async def test(np):
    n= int(np)
    res = engine.execute( "SELECT TOP {} * FROM [dbo].[rawdata3] ORDER BY NEWID() ".format(n)).fetchall()
    return {"result":res}

    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
