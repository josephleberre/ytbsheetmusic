# ytbsheetmusic

`ytbsheetmusic` is a web application that allows users to convert a music score from YouTube into a PDF file. This project is particularly useful for musicians who want to capture and organize sheet music from YouTube videos.

## Features

- **YouTube Video Download:** Download a YouTube video specified by its URL and save it locally.
- **Frame Extraction:** Capture specific frames from the video to create images of the sheet music.
- **Thumbnail Generation:** Create thumbnails for the downloaded videos.
- **Audio Extraction:** Extract audio from the video and save it as an MP3 file.
- **PDF Creation:** Assemble the extracted images into a PDF file containing the sheet music.
- **ZIP Archive Creation:** Compress the PDF file and MP3 audio into a ZIP archive.
- **Web Interface:** An intuitive user interface to manage conversions directly from your browser.

## Installation

### Prerequisites

- Python 3.7 or later
- `pip` for Python package management

### Clone the Repository

```bash
git clone https://github.com/josephleberre/ytbsheetmusic.git
cd ytbsheetmusic
```

### Install Dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

Configuration
Before starting the application, make sure to configure any necessary environment variables in a .env file if needed.

## Usage
Start the Flask Server:
Run the application with the following command:

```bash
python app.py
```
Access the Interface:
Open your web browser and go to http://localhost:5000.

### Download and Convert:

Enter the URL of the YouTube video containing the music score.
Choose the desired options for generating the score.
Click the button to start the process.
Download the final frames, the PDF or the ZIP archive containing the PDF and audio.
API
The application exposes several endpoints to interact with various functionalities:

## Disclaimer
This tool is intended primarily for educational purposes. The author is not responsible for any misuse of the tool. Users must respect intellectual property rights and adhere to YouTube's terms of service. Always ensure that you have the right to download and use the content you are converting.
