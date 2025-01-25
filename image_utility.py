from better_bing_image_downloader import downloader
from PIL import Image
import pandas as pd
import re
import os 
import shutil

def get_keywords_from_excel_file(file_name, additional_keywords):
    data_frame = pd.read_excel(file_name)
    return [f"{keyword} {" ".join(additional_keywords)}".strip() for keyword in data_frame['Subject'].tolist()]

def download_images_from_topic(topic_data):
    topic_name = topic_data['name'] 

    if os.path.exists(f"{topic_name}/images"):
        os.rmdir(f"{topic_name}/images")
        
    os.makedirs(f"{topic_name}/images")

    keywords = get_keywords_from_excel_file(f"{topic_name}/{topic_name}.xlsx", topic_data.get('additional_keywords', []))

    images_downloaded = []
    for keyword in keywords:
        keyword_folder = os.path.join(f"{topic_name}/images", keyword)
        requests_made = 0
        while (not os.path.exists(keyword_folder) or len(os.listdir(keyword_folder)) == 0) and requests_made < 50:
            downloader(
                query=keyword,
                limit=1,
                output_dir=f"{topic_name}/images",
                force_replace=True,
                verbose=False
            )
            requests_made += 1

        for file_name in os.listdir(keyword_folder):
            images_downloaded.append(keyword)
            source = os.path.join(keyword_folder, file_name)
            destination = os.path.join(f"{topic_name}/images", f"{keyword}.jpg")
            shutil.move(source, destination)
        os.rmdir(keyword_folder)
    
    print(f"{len(images_downloaded)} images downloaded for topic {topic_name}!")
    resize_images(f"{topic_name}/images")

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
        'name': 'underwater_and_sea',
    }
    #download_images_from_topic(TOPIC_DATA)
    #resize_images(f"{TOPIC_DATA['name']}/images")
    #rename_videos(TOPIC_DATA['name'])