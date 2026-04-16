"""
数据库模型定义
使用SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, BigInteger, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import get_settings
from loguru import logger

settings = get_settings()
Base = declarative_base()


class TrainingData(Base):
    """训练数据表"""
    __tablename__ = 'training_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False, comment='消息文本')
    is_spam = Column(Boolean, nullable=False, comment='是否为垃圾消息')
    source = Column(String(50), default='manual', comment='来源: manual-手动标记, auto-自动检测')
    chat_id = Column(BigInteger, nullable=True, comment='群组ID')
    message_id = Column(BigInteger, nullable=True, comment='消息ID')
    user_id = Column(BigInteger, nullable=True, comment='用户ID')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    __table_args__ = (
        Index('idx_is_spam', 'is_spam'),
        Index('idx_created_at', 'created_at'),
    )


class BannedUser(Base):
    """被封禁用户表"""
    __tablename__ = 'banned_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, unique=True, comment='用户ID')
    chat_id = Column(BigInteger, nullable=False, comment='群组ID')
    username = Column(String(100), nullable=True, comment='用户名')
    first_name = Column(String(100), nullable=True, comment='名字')
    violation_count = Column(Integer, default=1, comment='违规次数')
    reason = Column(String(255), nullable=True, comment='封禁原因')
    banned_at = Column(DateTime, default=datetime.utcnow, comment='封禁时间')
    unbanned_at = Column(DateTime, nullable=True, comment='解封时间')
    is_active = Column(Boolean, default=True, comment='是否仍被封禁')
    banned_by = Column(BigInteger, nullable=True, comment='操作管理员ID')

    __table_args__ = (
        Index('idx_user_chat', 'user_id', 'chat_id'),
        Index('idx_is_active', 'is_active'),
    )


class UserViolation(Base):
    """用户违规记录表"""
    __tablename__ = 'user_violations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    chat_id = Column(BigInteger, nullable=False, comment='群组ID')
    message_text = Column(Text, nullable=True, comment='违规消息内容')
    confidence = Column(String(20), nullable=True, comment='置信度')
    deleted_at = Column(DateTime, default=datetime.utcnow, comment='删除时间')
    is_banned = Column(Boolean, default=False, comment='是否已被封禁')

    __table_args__ = (
        Index('idx_user_violation', 'user_id', 'chat_id'),
    )


class GroupSettings(Base):
    """群组设置表"""
    __tablename__ = 'group_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, nullable=False, comment='群组ID')
    chat_title = Column(String(255), nullable=True, comment='群组标题')
    spam_threshold = Column(String(20), default='0.95', comment='垃圾消息阈值')
    max_violations = Column(Integer, default=3, comment='最大违规次数')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


# 数据库引擎和会话
engine = None
SessionLocal = None


def init_db():
    """初始化数据库"""
    global engine, SessionLocal
    engine = create_engine(
        settings.database_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("数据库初始化完成")


@contextmanager
def get_db_session() -> Session:
    """获取数据库会话上下文管理器"""
    if SessionLocal is None:
        init_db()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# 数据访问函数
def add_training_data(text: str, is_spam: bool, source: str = 'manual',
                      chat_id: int = None, message_id: int = None, user_id: int = None) -> TrainingData:
    """添加训练数据"""
    with get_db_session() as session:
        data = TrainingData(
            text=text,
            is_spam=is_spam,
            source=source,
            chat_id=chat_id,
            message_id=message_id,
            user_id=user_id
        )
        session.add(data)
        session.flush()
        session.refresh(data)
        return data


def get_training_data(limit: int = 100, offset: int = 0, is_spam: bool = None) -> list:
    """获取训练数据列表"""
    with get_db_session() as session:
        query = session.query(TrainingData)
        if is_spam is not None:
            query = query.filter(TrainingData.is_spam == is_spam)
        return query.order_by(TrainingData.created_at.desc()).offset(offset).limit(limit).all()


def count_training_data(is_spam: bool = None) -> int:
    """统计训练数据数量"""
    with get_db_session() as session:
        query = session.query(TrainingData)
        if is_spam is not None:
            query = query.filter(TrainingData.is_spam == is_spam)
        return query.count()


def add_banned_user(user_id: int, chat_id: int, username: str = None,
                   first_name: str = None, reason: str = None, banned_by: int = None) -> BannedUser:
    """添加封禁用户"""
    with get_db_session() as session:
        # 检查是否已存在
        existing = session.query(BannedUser).filter(
            BannedUser.user_id == user_id,
            BannedUser.chat_id == chat_id,
            BannedUser.is_active == True
        ).first()

        if existing:
            existing.violation_count += 1
            return existing

        banned = BannedUser(
            user_id=user_id,
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            reason=reason,
            banned_by=banned_by
        )
        session.add(banned)
        session.flush()
        session.refresh(banned)
        return banned


def get_banned_users(chat_id: int = None, is_active: bool = True, limit: int = 100, offset: int = 0) -> list:
    """获取封禁用户列表"""
    with get_db_session() as session:
        query = session.query(BannedUser)
        if chat_id:
            query = query.filter(BannedUser.chat_id == chat_id)
        if is_active is not None:
            query = query.filter(BannedUser.is_active == is_active)
        return query.order_by(BannedUser.banned_at.desc()).offset(offset).limit(limit).all()


def unban_user(user_id: int, chat_id: int) -> bool:
    """解封用户"""
    with get_db_session() as session:
        result = session.query(BannedUser).filter(
            BannedUser.user_id == user_id,
            BannedUser.chat_id == chat_id,
            BannedUser.is_active == True
        ).update({
            'is_active': False,
            'unbanned_at': datetime.utcnow()
        })
        return result > 0


def add_user_violation(user_id: int, chat_id: int, message_text: str = None,
                      confidence: float = None, is_banned: bool = False) -> UserViolation:
    """添加用户违规记录"""
    with get_db_session() as session:
        violation = UserViolation(
            user_id=user_id,
            chat_id=chat_id,
            message_text=message_text,
            confidence=str(confidence) if confidence else None,
            is_banned=is_banned
        )
        session.add(violation)
        session.flush()
        session.refresh(violation)
        return violation


def get_user_violation_count(user_id: int, chat_id: int) -> int:
    """获取用户违规次数"""
    with get_db_session() as session:
        return session.query(UserViolation).filter(
            UserViolation.user_id == user_id,
            UserViolation.chat_id == chat_id
        ).count()


def get_user_violations(user_id: int = None, chat_id: int = None, limit: int = 100, offset: int = 0) -> list:
    """获取违规记录列表"""
    with get_db_session() as session:
        query = session.query(UserViolation)
        if user_id:
            query = query.filter(UserViolation.user_id == user_id)
        if chat_id:
            query = query.filter(UserViolation.chat_id == chat_id)
        return query.order_by(UserViolation.deleted_at.desc()).offset(offset).limit(limit).all()


def get_or_create_group_settings(chat_id: int, chat_title: str = None) -> GroupSettings:
    """获取或创建群组设置"""
    with get_db_session() as session:
        settings = session.query(GroupSettings).filter(GroupSettings.chat_id == chat_id).first()
        if not settings:
            settings = GroupSettings(chat_id=chat_id, chat_title=chat_title)
            session.add(settings)
            session.flush()
            session.refresh(settings)
        elif chat_title and settings.chat_title != chat_title:
            settings.chat_title = chat_title
        return settings
