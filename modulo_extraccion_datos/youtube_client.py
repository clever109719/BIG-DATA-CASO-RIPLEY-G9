from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import API_KEY, QUERIES, MAX_VIDEOS, MAX_COMMENTS_PER_VIDEO

def get_youtube_service():
    return build("youtube", "v3", developerKey=API_KEY)

def fetch_comments(youtube, video_id):
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )
        while request and len(comments) < MAX_COMMENTS_PER_VIDEO:
            response = request.execute()
            for item in response.get("items", []):
                text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(text)
            request = youtube.commentThreads().list_next(request, response)
    except HttpError as e:
        print(f"No se pudieron obtener comentarios del video {video_id}: {e}")
    return comments

def fetch_videos(query):
    youtube = get_youtube_service()
    videos = []
    next_page_token = None
    while len(videos) < MAX_VIDEOS:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=min(50, MAX_VIDEOS - len(videos)),
            type="video",
            pageToken=next_page_token
        ).execute()
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            comments = fetch_comments(youtube, video_id)
            videos.append({
                "query": query,
                "id": video_id,
                "title": title,
                "comments": comments
            })
        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break
    return videos

def fetch_youtube_data():
    all_data_youtube = []
    for query in QUERIES:
        print(f"[YouTube] Buscando videos y comentarios para: {query}")
        data = fetch_videos(query)
        all_data_youtube.extend(data)
    return all_data_youtube

def count_videos_and_comments(youtube_data):
    total_videos = len(youtube_data)
    total_comments = sum(len(video["comments"]) for video in youtube_data)
    return total_videos, total_comments