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

def find_tags(element,tag, objtype, class_name): 
    # dùng kiếm lời nhạc, tên bài từ web lyrics.vn
    # param ex: <div class="details"> =>> tag="div", objtype="class", class_name="details"
    # element là văn bản html, String "class_name" là tên thẻ cần tìm trong các thẻ của văn bản html
    #tìm kiếm đệ quy, nếu tìm được thì trả về
    if element.name == tag and class_name in element.get(objtype, []):
        return element
    # nếu thẻ đang xét có các thẻ con? duyệt từng thẻ con bằng hàm đệ quy
    for child in element.children:
        if child.name:
            result = find_tags(child,tag,objtype, class_name)
            if result:
                return result
    #không thấy 
    return None

def find_artist_tag(soup):
    # kiếm tác giả từ web lyrics.vn
    h3_tags = soup.find_all('h3', class_='pull-left text-uppercase')
    if h3_tags:
        return h3_tags[0].text.strip().replace("Cùng tác giả ", "")
    else:
        return None

def crawl_data(url):
    #cào dữ liệu từ 1 đường link lyric.vn cụ thể
    data={}
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # phân tích cú pháp dữ liệu html bằng soup (why soup tho ??? who cooking ?)
    songname=find_tags(soup,"h3","class","bold")
    artist=find_artist_tag(soup)
    lyrics = find_tags(soup,"div","class","detail")
    # tìm thẻ detail trong văn bản html, hãy inspect = f12 để xem cần tìm thẻ nào.
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
        # không thấy lyrics là cook luôn 
        return
    
    them_ban_ghi(data) # thêm bản ghi vào elastic
    
def clean_and_concatenate_paragraphs(text):
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r'[,.!?"\'-]', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\r', ' ', text)
    text = ' '.join(text.split())
    return text

def remove_html_tags2(html_tag):
    soup = BeautifulSoup(html_tag, 'html.parser')
    # Loại bỏ các thẻ <br> và thay thế chúng bằng dấu xuống dòng
    #for br in soup.find_all('br'):
    #    br.replace_with('\n')
    # Lấy nội dung của thẻ và loại bỏ các thẻ HTML
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

read_file_line_by_line("linklist.txt")# thay bằng đường dẫn tới file chứa các link đẫn tới bài hát.