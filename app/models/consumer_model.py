from datetime import datetime

from . import db, ma

class Consumer(db.Model):
    __tablename__ = 'consumers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    user_id = db.Column(db.Integer, nullable=False)
    # user = db.relationship('User', backref=db.backref("consumers", single_parent=True, lazy=True))
    is_suspended = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetch_all(cls):
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def fetch_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def update(cls, id, name=None):
        record = cls.fetch_by_id(id)
        if name:
            record.name = name
        db.session.commit()
        return True

    @classmethod
    def suspend(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True

    @classmethod
    def restore(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        # record = cls.fetch_by_id(id)
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True

class ConsumerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'user_id', 'is_suspended', 'created', 'updated')
