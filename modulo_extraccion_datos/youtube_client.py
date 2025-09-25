from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import API_KEY, QUERY, MAX_VIDEOS, MAX_COMMENTS_PER_VIDEO

def get_youtube_service():
    return build("youtube", "v3", developerKey=API_KEY)

def fetch_videos():
    youtube = get_youtube_service()
    videos = []
    next_page_token = None

    while len(videos) < MAX_VIDEOS:
        search_response = youtube.search().list(
            q=QUERY,
            part="id,snippet",
            maxResults=min(50, MAX_VIDEOS - len(videos)),  # máximo permitido por API
            type="video",
            pageToken=next_page_token
        ).execute()

        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            comments = fetch_comments(youtube, video_id)
            videos.append({
                "id": video_id,
                "title": title,
                "comments": comments
            })

        # siguiente página
        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break  # ya no hay más resultados

    return videos


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
        # Si el video tiene comentarios deshabilitados o cualquier 403, lo saltamos
        print(f"⚠️  No se pudieron obtener comentarios del video {video_id}: {e}")

    return comments
