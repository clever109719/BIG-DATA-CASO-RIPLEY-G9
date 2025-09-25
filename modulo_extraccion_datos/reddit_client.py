# reddit_client.py
import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, QUERIES, MAX_REDDIT_COMMENTS

# Lista amplia de palabras clave para filtrar comentarios relevantes
KEYWORDS = [
    "ripley", "tienda", "tiendas", "compra", "compras", "comprar", 
    "producto", "productos", "servicio", "servicios", "atención", "soporte",
    "cliente", "clientes", "experiencia", "satisfacción", "insatisfacción",
    "bueno", "buena", "excelente", "malo", "mala", "deficiente", "terrible",
    "opinión", "opiniones", "recomendado", "no recomendable",
    "envío", "entrega", "devolución", "garantía", "precio", "precios", "oferta",
    "calidad", "demora", "rápido", "lento", "fraude", "estafa"
]

def get_reddit_client():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

def is_comment_relevant(comment):
    comment_lower = comment.lower()
    return "ripley" in comment_lower and any(keyword in comment_lower for keyword in KEYWORDS)

def fetch_reddit_data():
    reddit = get_reddit_client()
    all_data_reddit = []

    for query in QUERIES:
        for submission in reddit.subreddit("all").search(query, limit=20):
            submission.comments.replace_more(limit=0)
            comments_list = [c.body for c in submission.comments.list()[:MAX_REDDIT_COMMENTS]]
            # Filtrar solo comentarios relevantes
            relevant_comments = [c for c in comments_list if is_comment_relevant(c)]
            # Agregar el post si tiene al menos un comentario relevante
            if relevant_comments:
                all_data_reddit.append({
                    "query": query,
                    "id": submission.id,
                    "title": submission.title,
                    "comments": relevant_comments
                })

    return all_data_reddit

def count_posts_and_comments(reddit_data):
    total_posts = len(reddit_data)
    total_comments = sum(len(post["comments"]) for post in reddit_data)
    return total_posts, total_comments
