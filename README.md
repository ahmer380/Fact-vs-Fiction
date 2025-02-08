Steps per theme:
  1. Create Canva design
  2. Generate text content in Excel spreadsheet via chatGPT
  3. Run Python web-scraping script to find image for each subject, inject image into subject row via the command "=IMAGE("https://raw.githubusercontent.com/ahmer380/Fact-vs-Fiction/main/{topic_name}/images/" & A2 & ".jpg")

  4. Parse Excel spreadsheet to Canva "Bulk-Create" app to generate videos
  5. Run "Audio-Sync Pro" script in order to layer audio on to remaining videos
  6. Run Python file-renaming script for each generated video
