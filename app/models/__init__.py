"""
Database models
"""
from app.models.base import Base
from app.models.article import Article
from app.models.appointment import Appointment
from app.models.chat import ChatMessage
from app.models.faq import FAQ
from app.models.translation import TranslationCache, TranslationLog
from app.models.document import DocumentUpload
# 暂时跳过 ArticleEmbedding（需要 pgvector 扩展）
# from app.models.embedding import ArticleEmbedding

# Authentication and subscription models
from app.models.user import User, UserRole, AuthProvider
from app.models.email_verification import EmailVerification
from app.models.subscription import Subscription, SubscriptionLog, SubscriptionType, SubscriptionFrequency, SubscriptionStatus
from app.models.refresh_token import RefreshToken
from app.models.email_campaign import EmailCampaign, CampaignStatus

__all__ = [
    "Base",
    "Article",
    "Appointment",
    "ChatMessage",
    "FAQ",
    "TranslationCache",
    "TranslationLog",
    "DocumentUpload",
    # "ArticleEmbedding",
    # Authentication and subscription
    "User",
    "UserRole",
    "AuthProvider",
    "EmailVerification",
    "Subscription",
    "SubscriptionLog",
    "SubscriptionType",
    "SubscriptionFrequency",
    "SubscriptionStatus",
    "RefreshToken",
    "EmailCampaign",
    "CampaignStatus",
]

