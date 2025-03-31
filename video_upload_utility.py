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
            f"Youtube ID: {self.youtube_id}"
        )
    
    def __init__(self, video_index):
        #set the core attributes for the video object
        self.topic = TOPICS[video_index % len(TOPICS)]
        self.name = os.listdir(f"{self.topic}/videos")[video_index // len(TOPICS)].split(".")[0]
        self.path = f"{self.topic}/videos/{self.name}.mp4"
        self.upload_date = self.generate_upload_date(video_index)

        #set the genre-specific attributes for the video object
        self.tags = self.generate_tags()
        self.title = self.generate_title()
        self.description = self.generate_description()

        #modified once upload to platforms
        self.youtube_id = None
    
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

    def generate_description(self): #TODO: Link to other social medias when they are created
        return f"LIKE the short and hit the SUBSCRIBE button if you would like to learn more about the blueprint of our world! 🔥 \n {" ".join(self.tags)}"
    
class YoutubeApiService:
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

class TikTokApiService:
    def __init__(self):
        self.access_token = self.authenticate()
        self.current_video_index = self.generate_current_video_index()
    
    def authenticate(self):
        with open("tiktok_client_credentials.json", "r") as file:
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
        with open("tiktok_client_credentials.json", "w") as file:
            tiktok_credentials["cached_access_token"] = {
                "access_token": token_exhchange_response["access_token"],
                "expires_in": datetime.now().timestamp() + token_exhchange_response["expires_at"]
            }
            json.dump(tiktok_credentials, file, indent=4)
        
        print("New access token saved to tiktok_client_credentials.json! This will last for 24 hours.")
        return token_exhchange_response["access_token"]

    def upload_video(self, video: Video): #TODO: Upload video to TikTok
        print(f"{video.name} uploaded to TikTok")
        return video
    
    def generate_current_video_index(self): #TODO: Get the current video index from TikTok
        return 0 
    
def get_total_video_count(): #returns 203, although there are 204 videos
    return sum([len(os.listdir(f"{topic}/videos")) for topic in TOPICS]) // len(TOPICS) * len(TOPICS)

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
    selectedAPIService = TikTokApiService()
    videos = get_video_list(count=30, start_index=selectedAPIService.current_video_index)
    for video in videos:
        uploaded_video = selectedAPIService.upload_video(video)
        print('\n')

#57 Videos uploaded to youtube so far