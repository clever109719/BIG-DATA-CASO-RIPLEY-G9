from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import API_KEYS, QUERIES, MAX_VIDEOS, MAX_COMMENTS_PER_VIDEO

def get_youtube_client(api_key):
    return build("youtube", "v3", developerKey=api_key)

def fetch_videos(query, youtube):
    request = youtube.search().list(
        q=query,
        part="id,snippet",
        type="video",
        maxResults=MAX_VIDEOS
    )
    response = request.execute()
    return response.get("items", [])

def fetch_comments(video_id, youtube):
    try:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=MAX_COMMENTS_PER_VIDEO,
            textFormat="plainText"
        )
        response = request.execute()

        comments = []
        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comment = {
                "id": item["id"],
                "text": snippet["textDisplay"],
                "publishedAt": snippet["publishedAt"],
                "author": snippet.get("authorDisplayName"),
                "likes": snippet.get("likeCount", 0),
                "replies": []
            }

            # Procesar replies si existen
            if "replies" in item:
                for reply in item["replies"]["comments"]:
                    reply_snippet = reply["snippet"]
                    comment["replies"].append({
                        "id": reply["id"],
                        "text": reply_snippet["textDisplay"],
                        "publishedAt": reply_snippet["publishedAt"],
                        "author": reply_snippet.get("authorDisplayName"),
                        "likes": reply_snippet.get("likeCount", 0)
                    })

            comments.append(comment)

        return comments

    except Exception as e:
        if "commentsDisabled" in str(e):
            return []
        else:
            raise e

def fetch_youtube_data():
    all_data = []
    api_index = 0

    for query in QUERIES:
        print(f"[Youtube] Buscando videos y comentarios para: {query}")
        success = False
        attempts = 0
        while not success and attempts < len(API_KEYS):
            api_key = API_KEYS[api_index]
            youtube = get_youtube_client(api_key)
            try:
                videos = fetch_videos(query, youtube)
                for video in videos:
                    video_id = video["id"]["videoId"]
                    comments = fetch_comments(video_id, youtube)
                    all_data.append({
                        "query": query,
                        "video_id": video_id,
                        "title": video["snippet"]["title"],
                        "comments": comments
                    })
                success = True
            except HttpError as e:
                if e.resp.status == 403 and "quotaExceeded" in str(e):
                    print(f"[!] API Key agotada: {api_key}")
                    api_index = (api_index + 1) % len(API_KEYS)
                    attempts += 1
                else:
                    raise e
        if not success:
            print(f"[!] No se pudo completar la query '{query}' porque todas las API Keys se agotaron.")
            break

    return all_data

def count_videos_and_comments(youtube_data):
    total_videos = len(youtube_data)
    total_comments = 0

    for video in youtube_data:
        for comment in video["comments"]:
            total_comments += 1  
            total_comments += len(comment.get("replies", []))  

    return total_videos, total_comments