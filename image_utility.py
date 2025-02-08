from PIL import Image
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import os 
import shutil

def get_keywords_from_excel_file(file_name, additional_keywords):
    data_frame = pd.read_excel(file_name)
    return [f"{keyword} {" ".join(additional_keywords)}".strip() for keyword in data_frame['Subject'].tolist()]

def download_wiki_images_from_topic(topic_data):
    topic_name = topic_data['name'] 
    if os.path.exists(f"{topic_name}/images"):
        shutil.rmtree(f"{topic_name}/images")
        
    os.makedirs(f"{topic_name}/images")

    keywords = get_keywords_from_excel_file(f"{topic_name}/{topic_name}.xlsx", topic_data.get('additional_keywords', []))

    images_downloaded = []
    for keyword in keywords:
        url = f"https://en.wikipedia.org/wiki/{keyword}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        infobox = soup.find("table", {"class": "infobox"})
        og_image = soup.find("meta", property="og:image")
        if infobox:
            img_url = "https:" + infobox.find("img").get("src")
        elif og_image:
            img_url = og_image.get("content")
        else:
            img_url = None

        if img_url:
            headers = {
                "User-Agent": "MyImageDownloader/1.0 johndoe@example.org"
            }
            img_data = requests.get(img_url, headers=headers).content
            with open(f"{topic_name}/images/{keyword}.jpg", 'wb') as handler:
                handler.write(img_data)
            print(f"Downloaded wiki image for {keyword}!")
            images_downloaded.append(keyword)
        else:
            print(f"Could not find wiki image for {keyword}.")
    
    print(f"{len(images_downloaded)} images downloaded for topic {topic_name}!")

def resize_images(directory_path):
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        with Image.open(file_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            img.save(file_path)
    print(f"All images in {directory_path} have been resized to 512x512.")

def rename_videos(topic_name):
    video_folder = os.path.join(topic_name, 'videos')
    keywords = get_keywords_from_excel_file(f"{topic_name}/{topic_name}.xlsx", [])
    sorted_videos = sorted(os.listdir(video_folder), key=lambda x: int(re.search(r'\d+', x).group()))

    for video_file, keyword in zip(sorted_videos, keywords):
        old_path = os.path.join(video_folder, video_file)
        new_path = os.path.join(video_folder, f"{keyword}.mp4")
        os.rename(old_path, new_path)
    
    print(f"All images in {video_folder} have been renamed to match their contents")


if __name__ == '__main__':
    TOPIC_DATA = {
        'name': 'superheroes',
    }
    download_wiki_images_from_topic(TOPIC_DATA)
    #resize_images(f"{TOPIC_DATA['name']}/images")
    #rename_videos(TOPIC_DATA['name'])