"""
Pydantic schemas for request/response validation
"""
from app.schemas.auth import (
    LoginRequest, Token, TokenData,
    EmailLoginRequest, AdminLoginRequest, GoogleLoginRequest,
    TokenResponse, RefreshTokenRequest, RefreshTokenResponse,
    SendVerificationCodeRequest, VerifyCodeRequest, VerifyCodeResponse,
    PasswordResetRequest, GoogleAuthUrlResponse, GoogleCallbackRequest
)
from app.schemas.user import (
    UserCreate, UserUpdate, UserUpdatePassword,
    UserResponse, UserPublicResponse
)
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionUpdate,
    SubscriptionResponse, SubscriptionPublicResponse,
    SubscriptionConfirmResponse, SubscriptionUnsubscribeResponse,
    SubscriptionListQuery, SubscriptionListResponse,
    SubscriptionStatsResponse
)
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListItem,
    ArticleListResponse,
    RelatedArticlesResponse,
    ContentBlock
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse,
    AppointmentConfirmation,
    AvailableSlotsResponse,
    TimeSlot
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    ChatHistoryResponse,
    QuickQuestion,
    QuickQuestionsResponse,
    SourceReference
)
from app.schemas.faq import (
    FAQCreate,
    FAQUpdate,
    FAQResponse,
    FAQListResponse,
    FAQListItem,
    FAQSearchResponse,
    FAQSearchResult
)
from app.schemas.translation import (
    TranslateRequest,
    TranslateResponse,
    BatchTranslateRequest,
    BatchTranslateResponse,
    DetectLanguageRequest,
    DetectLanguageResponse,
    TranslationLogResponse,
    TranslationHistoryResponse
)
from app.schemas.document import (
    UploadDocumentRequest,
    UploadDocumentResponse,
    DocumentUploadHistoryResponse,
    DocumentUploadDetail,
    ParseResult
)

__all__ = [
    # Auth
    'LoginRequest',
    'Token',
    'TokenData',
    'EmailLoginRequest',
    'AdminLoginRequest',
    'GoogleLoginRequest',
    'TokenResponse',
    'RefreshTokenRequest',
    'RefreshTokenResponse',
    'SendVerificationCodeRequest',
    'VerifyCodeRequest',
    'VerifyCodeResponse',
    'PasswordResetRequest',
    'GoogleAuthUrlResponse',
    'GoogleCallbackRequest',

    # User
    'UserCreate',
    'UserUpdate',
    'UserUpdatePassword',
    'UserResponse',
    'UserPublicResponse',

    # Subscription
    'SubscriptionCreate',
    'SubscriptionUpdate',
    'SubscriptionResponse',
    'SubscriptionPublicResponse',
    'SubscriptionConfirmResponse',
    'SubscriptionUnsubscribeResponse',
    'SubscriptionListQuery',
    'SubscriptionListResponse',
    'SubscriptionStatsResponse',

    # Article
    'ArticleCreate',
    'ArticleUpdate',
    'ArticleResponse',
    'ArticleListItem',
    'ArticleListResponse',
    'RelatedArticlesResponse',
    'ContentBlock',

    # Appointment
    'AppointmentCreate',
    'AppointmentUpdate',
    'AppointmentResponse',
    'AppointmentListResponse',
    'AppointmentConfirmation',
    'AvailableSlotsResponse',
    'TimeSlot',

    # Chat
    'ChatRequest',
    'ChatResponse',
    'ChatMessageResponse',
    'ChatHistoryResponse',
    'QuickQuestion',
    'QuickQuestionsResponse',
    'SourceReference',

    # FAQ
    'FAQCreate',
    'FAQUpdate',
    'FAQResponse',
    'FAQListResponse',
    'FAQListItem',
    'FAQSearchResponse',
    'FAQSearchResult',

    # Translation
    'TranslateRequest',
    'TranslateResponse',
    'BatchTranslateRequest',
    'BatchTranslateResponse',
    'DetectLanguageRequest',
    'DetectLanguageResponse',
    'TranslationLogResponse',
    'TranslationHistoryResponse',

    # Document
    'UploadDocumentRequest',
    'UploadDocumentResponse',
    'DocumentUploadHistoryResponse',
    'DocumentUploadDetail',
    'ParseResult',
]
