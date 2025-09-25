from youtube_client import fetch_videos
from hdfs_client import save_to_hdfs
from config import OUTPUT_HDFS_PATH

def main():
    print("Buscando videos y comentarios en YouTube...")
    data = fetch_videos()

    print(f"Se obtuvieron {len(data)} videos. Guardando en HDFS...")
    save_to_hdfs(data, OUTPUT_HDFS_PATH)

if __name__ == "__main__":
    main()
