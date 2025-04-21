import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http
import json
import os
import pytz
import requests
import secrets
import subprocess
from datetime import datetime, timedelta

VIDEO_LIST_RELPATH = "resized_videos"

UNDERWATER_AND_SEA = "underwater_and_sea"
COUNTRIES = "countries"
CELEBRITIES = "celebrities"
WORLD_RECORDS = "world_records" 
VIDEO_GAMES = "video_games"
SUPERHEROES = "superheroes"
MATHEMATICS = "mathematics"

TOPICS = [UNDERWATER_AND_SEA, COUNTRIES, CELEBRITIES, WORLD_RECORDS, VIDEO_GAMES, SUPERHEROES, MATHEMATICS]

class Video:
    def __str__(self):
        return (
            f"Title: {self.title}\n"
            f"Topic: {self.topic}\n"
            f"Path: {self.path}\n"
            f"Upload Date: {self.upload_date}\n"
            f"Description: {self.description}\n"
            f"Tags: {self.tags}\n"
            f"Youtube ID: {self.youtube_id}\n",
            f"TikTok ID: {self.tiktok_id}"
        )
    
    def __init__(self, video_index):
        #set the core attributes for the video object
        self.topic = TOPICS[video_index % len(TOPICS)]
        self.name = os.listdir(f"{self.topic}/{VIDEO_LIST_RELPATH}")[video_index // len(TOPICS)].split(".")[0]
        self.path = f"{self.topic}/{VIDEO_LIST_RELPATH}/{self.name}.mp4"
        self.upload_date = self.generate_upload_date(video_index)

        #set the genre-specific attributes for the video object
        self.tags = self.generate_tags()
        self.title = self.generate_title()
        self.description = self.generate_description()

        #modified once upload to platforms
        self.youtube_id = None
        self.tiktok_id = None
    
    def generate_upload_date(self, video_index):
        HOUR_TO_UPLOAD = 16
        FIRST_UPLOAD_DATE = datetime.now(pytz.timezone('Europe/London')) + timedelta(days=1)
        upload_date =  (FIRST_UPLOAD_DATE + timedelta(days=video_index-selectedAPIService.current_video_index)).replace(hour=HOUR_TO_UPLOAD, minute=0, second=0, microsecond=0)
        return upload_date.isoformat()
    
    def generate_tags(self):
        tag_friendly_name = f"#{self.name.lower().replace(" ", "").replace("-", "")}"
        TAG_TEMPLATES = {
            UNDERWATER_AND_SEA: ["#shorts", tag_friendly_name, "#underwater"],
            COUNTRIES: ["#shorts", tag_friendly_name, "#countries"],
            CELEBRITIES: ["#shorts", tag_friendly_name, "#celebrities"],
            WORLD_RECORDS: ["#shorts", tag_friendly_name, "#worldrecords"],
            VIDEO_GAMES: ["#shorts", tag_friendly_name, "#gaming"],
            SUPERHEROES: ["#shorts", tag_friendly_name, "#superheroes"],
            MATHEMATICS: ["#shorts", "#quiz", "#math"]
        }
        return TAG_TEMPLATES[self.topic]

    def generate_title(self):
        TITLE_TEMPLATES = {
            UNDERWATER_AND_SEA: f"Fact Versus Fiction: {self.name}! 🌊",
            COUNTRIES: f"Fun Facts about {self.name}! 🌎",
            CELEBRITIES: f"Fun Facts about {self.name}! 🌟",
            WORLD_RECORDS: f"World Records about {self.name}! 🏆",
            VIDEO_GAMES: f"Fun Facts about {self.name}! 🎮",
            SUPERHEROES: f"Fun Facts about {self.name}! 🦸",
            MATHEMATICS: f"Quick Math Quiz! Beat the Clock! ⏳ (Part {self.name[11:].lstrip('0')})",
        }
        return TITLE_TEMPLATES[self.topic]

    def generate_description(self):
        return f"LIKE the short and hit the SUBSCRIBE button if you would like to learn more about the blueprint of our world! 🔥 \n {" ".join(self.tags)}"
    
class YoutubeApiService: #Manual Work: add thumbnail to video
    def __init__(self):
        self.playlist_ids = {
            UNDERWATER_AND_SEA: "PLF7zIEyatLch96oXpo_5T74lDKa0ixzTq",
            COUNTRIES: "PLF7zIEyatLcjr0WUmAW7wLDBKF9kpQKxh",
            CELEBRITIES: "PLF7zIEyatLciWJuuMidjCWPtNhW7AtWfl",
            WORLD_RECORDS: "PLF7zIEyatLchWVIDxbnD1szb0bzT8O5ji",
            VIDEO_GAMES: "PLF7zIEyatLcjNSZ6X4EHOtYCnH7DT_jOJ",
            SUPERHEROES: "PLF7zIEyatLcgYErOEiIgrItrfRmVL2td-",
            MATHEMATICS: "PLF7zIEyatLciRbZ71hEhWyCtwEOKRZmU_"
        }
        self.authenticate = self.authenticate()
        self.current_video_index = self.generate_current_video_index()
    
    def authenticate(self):
        client_secret_file_path = "youtube_client_credentials.json"
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secret_file_path, 
            scopes=[
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        )
        credentials = flow.run_local_server()
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    def upload_video(self, video: Video):
        request_body = {
            "snippet": {
                "title": video.title,
                "description": video.description,
                "tags": video.tags,
                "categoryId": 24 #Entertainment category
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": video.upload_date, 
                "selfDeclaredMadeForKids": False,
                "containsSyntheticMedia": False
            }
        }
        request = self.authenticate.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=googleapiclient.http.MediaFileUpload(video.path, chunksize=-1, resumable=True)
        )

        response = request.execute()
        if "error" in response:
            raise Exception(f"Error uploading video {video.name}: {response['error']['message']}")
        video.youtube_id = response["id"]
        print(f"{video.name} uploaded to Youtube")
        
        return self.add_video_to_playlist(video)

    def add_video_to_playlist(self, video: Video):
        assert video.youtube_id is not None, "Video must be uploaded to Youtube before adding to playlist"

        request_body = {
            "snippet": {
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video.youtube_id
                },
                "playlistId": self.playlist_ids[video.topic],
            }
        }
        request = self.authenticate.playlistItems().insert(
            part="snippet",
            body=request_body
        )

        response = request.execute()
        if "error" in response:
            raise Exception(f"Error adding video to playlist: {response['error']['message']}")
        print(f"{video.name} added to {video.topic} playlist")

        return video

    def generate_current_video_index(self):
        youtube_upload_count = 0
        for playlist_id in self.playlist_ids.values():
            request = self.authenticate.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id
            )
            response = request.execute()
            youtube_upload_count += len(response["items"])
        
        return youtube_upload_count

class TikTokApiService: #Bottlenecks: Cannot schedule video, cannot add to playlist
    def __init__(self):
        self.access_token = self.authenticate()
        self.current_video_index = self.generate_current_video_index()
    
    def authenticate(self):
        with open("video_upload_utilities/tiktok_client_credentials.json", "r") as file:
            tiktok_credentials = json.load(file)
            if tiktok_credentials.get("cached_access_token") and tiktok_credentials["cached_access_token"]["expires_at"] > datetime.now().timestamp():
                return tiktok_credentials["cached_access_token"]["access_token"]

        #1. Get the authorisation code
        authorisation_url = "".join([
            f"https://www.tiktok.com/v2/auth/authorize/?",
            f"client_key={tiktok_credentials['web']['client_key']}&",
            f"scope=video.list,video.publish,video.upload&",
            f"redirect_uri={tiktok_credentials['web']['redirect_uri']}&",
            f"state={secrets.token_urlsafe(30)}&",
            f"response_type=code",
        ])
        print("Please authorise uploading to TikTok by:")
        print(f"Visiting the following URL and accepting the permissions: {authorisation_url}")
        print("Then copy the authorisation code from the redirected URL and paste it here:")
        authorisation_code = input("Authorisation code: ")

        #2. Use the authorisation code to get the access token
        token_exchange_payload = {
            f"client_key": tiktok_credentials["web"]["client_key"],
            f"client_secret": tiktok_credentials["web"]["client_secret"],
            f"code": authorisation_code,
            f"grant_type": "authorization_code",
            f"redirect_uri": tiktok_credentials["web"]["redirect_uri"],
        }
        token_exhchange_response = requests.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data=token_exchange_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ).json()
        if token_exhchange_response.get("error"):
            raise Exception(f"Error getting access token: {token_exhchange_response["error_description"]} \n Are you sure you pasted the correct authorisation code?")

        
        #3. Write access token to "tiktok_client_credentials.json"
        with open("video_upload_utilities/tiktok_client_credentials.json", "w") as file:
            tiktok_credentials["cached_access_token"] = {
                "access_token": token_exhchange_response["access_token"],
                "expires_at": datetime.now().timestamp() + token_exhchange_response["expires_in"]
            }
            json.dump(tiktok_credentials, file, indent=4)
        
        print("New access token saved to tiktok_client_credentials.json! This will last for 24 hours.")
        return token_exhchange_response["access_token"]

    def upload_video(self, video: Video): 
        #1. Configuring the video metadata to get the upload_url
        get_upload_url_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json ;charset=UTF-8",
        }
        get_upload_url_request_body = {
            "post_info": {
                "privacy_level": "SELF_ONLY",
                "title": video.title,
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False,
                "video_cover_timestamp_ms": 1500,
                "brand_content_toggle": False,
                "brand_organic_toggle": False,
                "is_aigc": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": os.path.getsize(video.path),
                "chunk_size": os.path.getsize(video.path),
                "total_chunk_count": 1,
            }
        }
        get_upload_url_response = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers=get_upload_url_headers,
            json=get_upload_url_request_body
        ).json()
        if get_upload_url_response['error']['code'] != "ok":
            raise Exception(f"Error uploading video {video.name}: {get_upload_url_response['error']['message']}")
        
        #2. Sending the video's path to the upload_url
        send_video_headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(os.path.getsize(video.path)),
            "Content-Range": f"bytes 0-{os.path.getsize(video.path)-1}/{os.path.getsize(video.path)}",
        }
        send_video_response = requests.put(
            get_upload_url_response['data']['upload_url'],
            headers=send_video_headers,
            data=open(video.path, "rb").read()
        )
        if send_video_response.status_code != 201:
            raise Exception(f"Error uploading video {video.name}: {send_video_response.text}")

        print(f"{video.name} uploaded to TikTok")
        return video
    
    def generate_current_video_index(self):
        tiktok_upload_count = 0
        cursor = None
        while True:
            get_video_list_response = requests.post(
                "https://open.tiktokapis.com/v2/video/list/", #Only relies upon publically listed videos... not helpful!
                headers={"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"},
                params={"fields": "id,title"},
                json={"cursor": cursor, "max_count": 20}
            ).json()
            if get_video_list_response['error']['code'] != "ok":
                raise Exception(f"Error connecting to TikTok list API: {get_video_list_response['error']['message']}")
            cursor = get_video_list_response['data']['cursor']
            tiktok_upload_count += len(get_video_list_response['data']['videos'])
            if not get_video_list_response['data']['has_more']:
                return tiktok_upload_count
    
def get_total_video_count(): #returns 203, although there are 204 videos
    return sum([len(os.listdir(f"{topic}/{VIDEO_LIST_RELPATH}")) for topic in TOPICS]) // len(TOPICS) * len(TOPICS)

def get_video_list(count=None, start_index=0):
    if not count:
        count = get_total_video_count()-start_index
    assert count > 0, "count must be greater than 0"
    assert start_index >= 0, "start_index must be greater than or equal to 0"
    assert start_index + count <= get_total_video_count(), f"start_index ({start_index}) + count ({count}) must be less than or equal to total video count of {get_total_video_count()}"

    return [Video(index) for index in range(start_index, start_index + count)]

def resize_video_file(video: Video):
    #The original video files are saved on the google drive, so we may overwrite these ones
    command = f'ffmpeg -i "{video.path}" -vf pad=1080:2040:0:120:black -c:a copy "temp.mp4"'
    subprocess.run(command, shell=True, check=True)
    os.replace("temp.mp4", video.path)

if __name__ == '__main__':
    selectedAPIService = TikTokApiService() #must be instantiated prior to generating the video objects
    videos = get_video_list(count=1, start_index=selectedAPIService.current_video_index)
    for video in videos:
        uploaded_video = selectedAPIService.upload_video(video)
        print('\n')

#57 videos uploaded to youtube so far
#12 videos uploaded to tiktok so far
