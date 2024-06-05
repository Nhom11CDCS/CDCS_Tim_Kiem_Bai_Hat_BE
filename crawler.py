from bs4 import BeautifulSoup
import requests
import re
import json
import os
import string 
from elasticsearch import Elasticsearch
#import es

#-------------------------------------------------
#Note: cái này để thêm dữ liệu vào elastic làm vốn
#This one just to add some e.g to the elastic 

def find_tags(element,tag, objtype, class_name): 
    # we crawl the lyrics fro website: lyrics.vn 
    # param ex: <div class="details"> =>> tag="div", objtype="class", class_name="details"
    # element is html, String "class_name" is html tag whhich is being found
    #recursive searching, return if successfully find
    if element.name == tag and class_name in element.get(objtype, []):
        return element
    # use recursion here 
    for child in element.children:
        if child.name:
            result = find_tags(child,tag,objtype, class_name)
            if result:
                return result
    #fail to check
    return None

def find_artist_tag(soup):
    # find artist name in lyrics.vn
    h3_tags = soup.find_all('h3', class_='pull-left text-uppercase')
    if h3_tags:
        return h3_tags[0].text.strip().replace("Cùng tác giả ", "")
    else:
        return None

def crawl_data(url):
    #crawl data from a specific link
    data={}
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # analyize with  soup (why soup tho ??? who cooking ?)
    songname=find_tags(soup,"h3","class","bold")
    artist=find_artist_tag(soup)
    lyrics = find_tags(soup,"div","class","detail")
    # find detail tag in html, use inspect here 
    if songname:
        txt=remove_html_tags2(songname.text)
        data["song_name"]=txt
    else:
        print("+ Songname not found.")
        data["song_name"]="no data"
    
    if artist:
        txt=remove_html_tags2(artist)
        data["artist"]=txt
    else:
        print("+ artist not found.")
        data["artist"]="no data"
    
    if lyrics:
        txt=remove_html_tags2(lyrics.text)
        #print(txt)
        txt1=clean_and_concatenate_paragraphs(txt)
        #print(txt1)
        data["lyrics"]= txt1
    else:
        print("+ lyrics not found.")
        # return if cannot find the lyrics
        return
    
    them_ban_ghi(data) # add new index 
    
def clean_and_concatenate_paragraphs(text):
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r'[,.!?"\'-]', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\r', ' ', text)
    text = ' '.join(text.split())
    return text

def remove_html_tags2(html_tag):
    soup = BeautifulSoup(html_tag, 'html.parser')
    # remove <br> 
    #for br in soup.find_all('br'):
    #    br.replace_with('\n')
    # get context and remove HTML tags 
    content = soup.get_text(separator=' ', strip=True)
    return content

def read_file_line_by_line(filename):
    try:
        with open(filename, 'r') as file:
            for line in file:
                #print(line.strip())  # strip() is used to remove any trailing newline character
                crawl_data(line.strip())
    except FileNotFoundError:
        print("File not found:", filename)
    except Exception as e:
        print("An error occurred:", e)

def them_ban_ghi(record):
    es = Elasticsearch("http://localhost:9200")  
    response = es.index(index="songs_index", body=record)
    print(response.get('result'))

read_file_line_by_line("/home/clayzzz/Desktop/CDCS_Tim_Kiem_Bai_Hat_BE/link.txt")# replace with the link to your file containing links t.