import os
import google_auth_oauthlib.flow
import googleapiclient.http
import pytz
from datetime import datetime, timedelta
import google_auth_oauthlib.flow
import googleapiclient.discovery
import subprocess

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
        HOUR_TO_UPLOAD = 10
        FIRST_UPLOAD_DATE = datetime.now(pytz.timezone('Europe/London')) + timedelta(days=1)
        upload_date =  (FIRST_UPLOAD_DATE + timedelta(days=video_index)).replace(hour=HOUR_TO_UPLOAD, minute=0, second=0, microsecond=0)
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
        return f"{TITLE_TEMPLATES[self.topic]} {" ".join(self.tags)}"

    def generate_description(self): #TODO: Link to other social medias when they are created
        return f"like & subscribe :)"
    
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
        
        return video

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

    def get_current_video_index(self):
        youtube_upload_count = 0
        for playlist_id in self.playlist_ids.values():
            request = self.authenticate.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id
            )
            response = request.execute()
            youtube_upload_count += len(response["items"])
        
        return youtube_upload_count

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
    youtubeAPIService = YoutubeApiService()
    videos = get_video_list(count=30, start_index=youtubeAPIService.get_current_video_index())
    for video in videos:
        uploaded_video = youtubeAPIService.upload_video(video)
        youtubeAPIService.add_video_to_playlist(uploaded_video)
        print('\n')

#30 Videos schedule to be updloaded to youtube so far
#TODO: Thumbnails? Otherwise just do set them manually
#TODO: Scheduling date may become problematic if the script is not run on the day of the first upload