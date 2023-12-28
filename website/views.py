# Import necessary modules and libraries
from flask import Blueprint, render_template, session, request, redirect, url_for, send_file
from pytube import YouTube
from io import BytesIO

# Create a Blueprint named 'views' for the application views
views = Blueprint('views', __name__)

# Define a route for the home page (GET and POST requests)
@views.route('/', methods=['GET', 'POST'])
def home():
    # Handle POST request for form submission
    if request.method == 'POST':
        # Store the submitted link and link type in the session
        session["link"] = request.form.get('linkInput')

        try:
            # Attempt to retrieve information from a YouTube link
            url = YouTube(session["link"])
            url.check_availability()
            video_title = url.title
            thumbnail_url = url.thumbnail_url
            video_streams = url.streams.filter(file_extension='mp4', progressive=True).all()
            audio_streams = url.streams.filter(only_audio=True).all()
        except Exception as e:
            # Render an error page if there is an issue with the YouTube link
            return render_template('error.html', error_message=str(e))

        # Render the home page with retrieved information
        return render_template('download.html', title=video_title, thumbnail=thumbnail_url, video_streams=video_streams,
                               audio_streams=audio_streams)

    # Render the default index.html page for GET requests
    return render_template("index.html")

# Define a route for downloading videos or audio
@views.route('/download', methods=["POST"])
def download():
    # Handle POST request for download form submission
    if request.method == "POST":
        try:
            # Retrieve YouTube information from the stored link in the session
            url = YouTube(session["link"])
            download_type = request.form.get('downloadType')

            # Check the download type and get the corresponding stream
            itag = int(request.form.get('videoQuality' if download_type == 'video' else 'audioQuality'))
            stream = url.streams.get_by_itag(itag)

            # Check if a valid stream is obtained
            if not stream:
                return render_template('error.html', error_message='Invalid quality selected.')

            # Create a BytesIO buffer and stream the file into it
            buffer = BytesIO()
            stream.stream_to_buffer(buffer)
            buffer.seek(0)

            # Determine the appropriate filename and mimetype for the download
            filename = 'video.mp4' if download_type == 'video' else 'audio.mp3'
            mimetype = 'video/mp4' if download_type == 'video' else 'audio/mp3'
            return send_file(buffer, as_attachment=True, download_name=filename, mimetype=mimetype)
        except Exception as e:
            # Handle any exceptions that occur during the download process
            return render_template('error.html', error_message='An error occurred during download. ' + str(e))

    # Redirect to the home page if the request is not a POST request
    return redirect(url_for('views.home'))
