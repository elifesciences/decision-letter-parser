from elifearticle.article import Article


def base_sub_article(title, article_type, article_id):
    sub_article = Article(None, title)
    sub_article.article_type = article_type
    sub_article.id = article_id
    # dynamically set content_blocks until this property is added to the Article object properly
    sub_article.content_blocks = []
    return sub_article


def base_decision_letter():
    return base_sub_article(
        "Decision letter",
        "decision-letter",
        "sa1",
    )


def base_author_response():
    return base_sub_article("Author response", "reply", "sa2")
