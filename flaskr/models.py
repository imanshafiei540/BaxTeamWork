from app import db


class BlogPost(db.model):

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.column (db.string, nullable=False )
    description = db.column (db.string, nullable=False )

    def __init__(self, title, description):
        self.title = title
        self.description = description

    def __repr__(self):
        return '<title {}'.format(self.title)