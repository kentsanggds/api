from app import db
from app.dao.decorators import transactional
from app.models import Article


@transactional
def dao_create_article(article):
    db.session.add(article)


@transactional
def dao_update_article(article_id, **kwargs):
    return Article.query.filter_by(id=article_id).update(
        kwargs
    )


def dao_get_articles():
    return Article.query.order_by(Article.old_id).all()


def dao_get_article_by_id(article_id):
    return Article.query.filter_by(id=article_id).one()
