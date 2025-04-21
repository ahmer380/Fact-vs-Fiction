# The World Blueprint: A Semi-Automated Content Creator

**The World Blueprint** aims to be an educational-driven content creator, intending to `explore every facet of Earth — from its rich history and diverse cultures to the scientific and environmental marvels shaping our lives. Whether you're a curious learner or simply passionate about understanding our planet, join us on a daily journey of discovery.` - *YouTube bio description*

## Fact vs Fiction

The contents of this repository have been utilised to assist the creation & uploading of the `Fact vs Fiction` playlists (the premiere genre for the channel). The format of each (subject) video is simple: display statement (5s), display answer proving/disproving of statement (7s), repeat 3 times ≈ 36s duration. 

These videos were creation in bulk (29 videos per topic, for 7 topics = 204 `Fact vs Fiction` videos in total). The exact procedure for each `topic` is as follows: 
  1. Create [Canva](https://www.canva.com/) design template for `topic`
  2. Generate text content in Excel spreadsheet (path=`{topic}/{topic}.xlsx`) via chatGPT for each subject in `topic`. *This took the longest amount of time due to continuously re-prompting the ChatGPT model!!!*
  3. Run `download_wiki_images_from_topic` function in `video_creation_utility.py` in order to web-scrape image for each subject in `topic`. Followed by injecting the image into the subject row via the Excel command `=IMAGE("https://raw.githubusercontent.com/ahmer380/Fact-vs-Fiction/main/{topic_name}/images/" & A2 & ".jpg")`
  4. Parse Excel spreadsheet to [Canva "Bulk-Create" app](https://www.canva.com/help/bulk-create/) in order to generate the .mp4 files for all subjects in `topic`. *Unfortunately we are not just done yet! There appears to be an existing issue where [audio is not retained upon bulk create](https://www.reddit.com/r/canva/comments/13txr11/bulk_create_not_retaining_audio/)*
  5. Run [Audio-Sync Pro script](https://www.youtube.com/watch?v=6IKuJBY_aPQ) in order to layer audio on to each .mp4 subject file in `topic`
  6. Run `rename_videos` function in `video_creation_utility.py` for each .mp4 subject file in `topic`

Finally, after all .mp4 files have been generated, I run the `video_upload_utilities/upload.py` script in order to automatically (well sort of...) upload the files to their relevant platforms. Have a look at its separate [README.md file](dummy) for more information.

**Fact vs Fiction Topics: [Underwater and Sea, Countries, Celebrities, World Records, Video Games, Superheroes, Mathematics], 204 videos scheduled for upload**

## Platforms
- **YouTube:** [TheWorldBlueprint](https://www.youtube.com/@TheWorldBlueprint)
- **TikTok:** [the_world_blueprint](https://www.tiktok.com/@the_world_blueprint)
- **Instagram:** Coming soon!