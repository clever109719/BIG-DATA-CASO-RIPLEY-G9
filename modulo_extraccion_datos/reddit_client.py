import praw
from datetime import datetime
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, QUERIES, MAX_REDDIT_COMMENTS

KEYWORDS = [
    "ripley", "tienda", "tiendas", "compra", "compras", "comprar", 
    "producto", "productos", "servicio", "servicios", "atención", "soporte",
    "cliente", "clientes", "experiencia", "satisfacción", "insatisfacción",
    "bueno", "buena", "excelente", "malo", "mala", "deficiente", "terrible",
    "opinión", "opiniones", "recomendado", "no recomendable",
    "envío", "entrega", "devolución", "garantía", "precio", "precios", "oferta",
    "calidad", "demora", "rápido", "lento", "fraude", "estafa",
    "promoción", "promociones", "descuento", "descuentos", "rebaja", "rebajas",
    "compra online", "ecommerce", "virtual", "página web", "aplicación", "app",
    "tarjeta", "crédito", "intereses", "financiamiento", "banco",
    "cambio", "cambios", "reembolso", "postventa", "post-venta",
    "tecnología", "electrodoméstico", "electrodomésticos", "ropa", "moda", "muebles",
    "espera", "cola", "retraso", "demorado", "stock", "agotado",
    "feliz", "contento", "satisfecho", "insatisfecho", "enojado", "molesto",
    "reclamo", "queja", "quejas", "problema", "problemas"
]

def get_reddit_client():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

def is_comment_relevant(comment_text):
    comment_lower = comment_text.lower()
    return "ripley" in comment_lower and any(keyword in comment_lower for keyword in KEYWORDS)

def parse_comment(c):
    return {
        "id": c.id,
        "text": c.body,
        "publishedAt": datetime.utcfromtimestamp(c.created_utc).isoformat(),
        "author": c.author.name if c.author else None,
        "score": c.score,
        "replies": [parse_comment(r) for r in c.replies]
    }

def fetch_reddit_data():
    reddit = get_reddit_client()
    all_data_reddit = []

    for query in QUERIES:
        print(f"[Reddit] Buscando posts y comentarios para: {query}")
        for submission in reddit.subreddit("all").search(query, limit=20):
            submission.comments.replace_more(limit=0)
            all_comments = submission.comments.list()[:MAX_REDDIT_COMMENTS]

            relevant_comments = [c for c in all_comments if is_comment_relevant(c.body)]
            
            if relevant_comments:
                all_data_reddit.append({
                    "query": query,
                    "id": submission.id,
                    "title": submission.title,
                    "comments": [parse_comment(c) for c in relevant_comments]
                })

    return all_data_reddit

def count_posts_and_comments(reddit_data):
    total_posts = len(reddit_data)
    total_comments = 0

    for post in reddit_data:
        for comment in post["comments"]:
            total_comments += 1  
            total_comments += len(comment.get("replies", []))  

    return total_posts, total_comments
