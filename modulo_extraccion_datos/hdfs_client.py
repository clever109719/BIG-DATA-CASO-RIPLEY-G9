from hdfs import InsecureClient
import json

def save_to_hdfs(data, hdfs_path, url="http://localhost:9870", user="hadoop"):
    client = InsecureClient(url, user=user)
    with client.write(hdfs_path, encoding="utf-8", overwrite=True) as writer:
        json.dump(data, writer, ensure_ascii=False, indent=2)
    print(f"Archivo guardado en HDFS: {hdfs_path}")
