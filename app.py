from flask import Flask, request
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from transformers import pipeline

app = Flask(__name__)

@app.get('/summary')
def summary_api():
    url = request.args.get('url', '')
    video_id = url.split('=')[1]
    transcript = get_transcript(video_id)
    if transcript is None:
        return "Sorry, we were unable to generate a summary for this video because the transcript is unavailable or not in English Laguage. Please try another video or check if the transcript is available in English.", 400
    summary = get_summary(transcript)
    if not summary.strip():
        return "Sorry, we were unable to generate a summary for this video due to a technical issue. Please try again later or choose another video.", 500
    return summary, 200

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    for transcript in transcript_list:
        if transcript['language'] == 'en':
            return ' '.join([d['text'] for d in transcript_list])
    return None

def get_summary(transcript):
    summarizer = pipeline('summarization', model="sshleifer/distilbart-cnn-12-6")
    summary = ' '
    for i in range(0, (len(transcript)//1000)+1):
        summary_text = summarizer(transcript[i*1000:(i+1)*1000], max_length=100, min_length=10, do_sample=False)[0]['summary_text']
        summary = summary + summary_text + ' '
    return summary


if __name__ == '__main__':
    app.run(debug=True)