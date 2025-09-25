from youtube_client import fetch_videos
from hdfs_client import save_to_hdfs
from config import OUTPUT_HDFS_PATH, QUERIES

def main():
    all_data = []
    for query in QUERIES:
        print(f"🔎 Buscando videos y comentarios para: {query}...")
        data = fetch_videos(query)
        print(f"   → Se obtuvieron {len(data)} videos para '{query}'")
        all_data.extend(data)

    print(f"\nTotal videos recolectados: {len(all_data)}. Guardando en HDFS...")
    save_to_hdfs(all_data, OUTPUT_HDFS_PATH)

if __name__ == "__main__":
    main()
