from better_bing_image_downloader import downloader
import pandas as pd
import os 
import shutil

def get_keywords_from_excel_file(file_name, additional_keywords):
    data_frame = pd.read_excel(file_name)
    return [f"{keyword} {" ".join(additional_keywords)}".strip() for keyword in data_frame['Subject'].tolist()]

def download_images_from_topic(topic, additional_keywords=[]):
    if os.path.exists(f"{topic}/images"):
        os.rmdir(f"{topic}/images")
        
    os.makedirs(f"{topic}/images")

    keywords = get_keywords_from_excel_file(f"{topic}/{topic}.xlsx", additional_keywords)

    images_downloaded = []
    for keyword in keywords:
        keyword_folder = os.path.join(f"{topic}/images", keyword)
        requests_made = 0
        while (not os.path.exists(keyword_folder) or len(os.listdir(keyword_folder)) == 0) and requests_made < 50:
            downloader(
                query=keyword,
                limit=1,
                output_dir=f"{topic}/images",
                force_replace=True,
                verbose=False
            )
            requests_made += 1

        for file_name in os.listdir(keyword_folder):
            images_downloaded.append(keyword)
            source = os.path.join(keyword_folder, file_name)
            destination = os.path.join(f"{topic}/images", f"{keyword}.jpg")
            shutil.move(source, destination)
        os.rmdir(keyword_folder)
    
    print(f"{len(images_downloaded)} images downloaded for topic {topic}!")

if __name__ == '__main__':
    TOPICS = [('underwater_and_sea',)]
    for topic_data in TOPICS:
        download_images_from_topic(*topic_data)

