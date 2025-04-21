# (Semi) Automatically Uploading the Videos

After the video creation process, we are left with 204 .mp4 files at our disposal. We *could* manually upload each video to the relevant social media platform, but this would be very time-consuming, and not provide much flexibility if/when the methodology of our video upload algorithm evolves. `upload.py` is an automation script intended to upload any list of mp4 `videos` to any `social_media_platform`, scheduled to be published daily when possible.

## Uploading to YouTube
This can be done by setting `selectedAPIService` to  `YoutubeAPIService`, as well as configuring the correct credentials stored in the `youtube_client_credentials.json` file 

### API Features
- Upload to public account ✅
- Require no manual intervention ❌
- Schedule video ✅
- Set video to playlist ✅
- Set video thumbnail ❌ (only via thumbnail image upload, which was not done here)
- API quota definition: 1+ million credits per day 

## Uploading to TikTok
This can be done by setting `selectedAPIService` to  `TiktokAPIService`, as well as configuring the correct credentials stored in the `tikok_client_credentials.json` file 

### API Features
- Upload to public account ❌
- Require no manual intervention ✅ (assuming access token has not expired)
- Schedule video ❌
- Set video to playlist ❌
- Set video thumbnail ✅ (only via video timeframe image)
- API quota definition: Max 6 API requests per minute
