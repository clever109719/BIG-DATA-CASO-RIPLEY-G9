from youtube_client import fetch_youtube_data, count_videos_and_comments
from reddit_client import fetch_reddit_data, count_posts_and_comments
from hdfs_client import save_to_hdfs
from config import OUTPUT_YOUTUBE_HDFS_PATH, OUTPUT_REDDIT_HDFS_PATH

def main():
    # YouTube
    #all_youtube = fetch_youtube_data()
    #save_to_hdfs(all_youtube, OUTPUT_YOUTUBE_HDFS_PATH)
    #total_videos, total_comments = count_videos_and_comments(all_youtube)
    #print(f"[YouTube] Total videos: {total_videos}, Total comentarios: {total_comments}")

    # Reddit
    all_reddit = fetch_reddit_data()
    save_to_hdfs(all_reddit, OUTPUT_REDDIT_HDFS_PATH)
    total_posts, total_comments_reddit = count_posts_and_comments(all_reddit)
    print(f"[Reddit] Total posts: {total_posts}, Total comentarios: {total_comments_reddit}")

if __name__ == "__main__":
    main()
