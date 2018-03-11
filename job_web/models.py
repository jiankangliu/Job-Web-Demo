from datetime import datetime
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user

db = SQLAlchemy()

job_delivery = db.Table(
    'job_delivery',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id', ondelete='CASCADE'))
)

FINANCE_STAGE = ['未融资', '天使轮', 'A轮', 'B轮', 'C轮', 'D轮及以上', '上市公司', '不需要融资']
FIELD = ['移动互联网', '电子商务', '金融', '企业服务', '教育', '文化娱乐', '游戏', 'O2O', '硬件']
EXP = ['不限', '1年及以下', '1-3年', '3-5年', '5-10年', '10年以上']
EDUCATION = ['不限学历', '专科', '本科', '硕士', '博士']
DEFAULT_LOGO = 'https://www.zhipin.com/v2/chat_v2/images/v2/defaultlogov2.jpg'

ROLE_USER = 10
ROLE_COMPANY = 20
ROLE_ADMIN = 30


class Base(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime,
                           default=datetime.now,
                           onupdate=datetime.now)

    def __repr__(self):
        return '<{}: {}'.format(__class__.__name__, self.title)


class UserBase(Base, UserMixin):
    __abstract__ = True

    email = db.Column(db.String(64), unique=True, nullable=False)
    # phone = db.Column(db.Integer, unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)
    is_enable = db.Column(db.Boolean, default=True, index=True)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def is_user(self):
        return self.role == ROLE_USER

    def is_company(self):
        return self.role == ROLE_COMPANY

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def check_password(self, password):
        return check_password_hash(self._password, password)


class User(UserBase):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    resume = db.Column(db.String(128))
    role = db.Column(db.SmallInteger, default=ROLE_USER)


class Company(UserBase):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    website = db.Column(db.String(64))
    address = db.Column(db.String(128))
    logo = db.Column(db.String(256), default=DEFAULT_LOGO)
    role = db.Column(db.SmallInteger, default=ROLE_COMPANY)
    # 融资进度
    finance_stage = db.Column(db.String(16))
    # 公司领域
    field = db.Column(db.String(64))
    # 简介
    description = db.Column(db.String(256))
    # 详情
    details = db.Column(db.Text)

    def enabled_jobs(self):
        return self.jobs.filter(Job.is_enable.is_(True))


class Job(Base):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    salary_min = db.Column(db.SmallInteger, nullable=False, index=True)
    salary_max = db.Column(db.SmallInteger, nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), index=True)
    company = db.relationship('Company', uselist=False, backref=db.backref('jobs', lazy='dynamic'))
    # 职位描述
    description = db.Column(db.Text)
    # 职位待遇
    treatment = db.Column(db.Text)
    # 经验要求
    exp = db.Column(db.String(16), nullable=False, index=True)
    # 学历要求
    education = db.Column(db.String(16), nullable=False, index=True)
    # 工作城市
    city = db.Column(db.String(8))
    # 职位标签
    tags = db.Column(db.String(64))
    # 职位上线
    is_enable = db.Column(db.Boolean, default=True, index=True)

    @property
    def url(self):
        return url_for('job.detail', course_id=self.id)

    @property
    def tag_list(self):
        return self.tags.split(",")

    def current_user_is_applied(self):
        delivery = Delivery.query.filter_by(job_id=self.id, user_id=current_user.id).first()
        return delivery is not None


class Delivery(Base):
    __tablename__ = 'delivery'

    STATUS_WAITTING = 1
    STATUS_REJECT = 2
    STATUS_ACCEPT = 3

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', ondelete='SET NULL'), index=True)
    job = db.relationship('Job', uselist=False, backref=db.backref('delivery', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), index=True)
    user = db.relationship('User', uselist=False, backref=db.backref('delivery', lazy='dynamic'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='SET NULL'), index=True)
    company = db.relationship('Company', uselist=False, backref=db.backref('delivery', lazy='dynamic'))
    status = db.Column(db.SmallInteger, default=STATUS_WAITTING, index=True)
    company_response = db.Column(db.String(256))

    # @property
    # def user(self):
    #     return User.query.get(self.user_id)
    #
    # @property
    # def job(self):
    #     return Job.query.get(self.job_id)