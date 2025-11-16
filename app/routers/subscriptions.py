"""
Subscription router for email subscription management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate,
    SubscriptionListResponse
)
from app.services.subscription import SubscriptionService
from app.core.deps import require_admin
from app.models.user import User
from app.models.subscription import SubscriptionStatus, SubscriptionType

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# ============================================================================
# Public Endpoints
# ============================================================================

@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new email subscription
    
    **Public endpoint** - No authentication required
    
    **Request Body:**
    - **email**: Email address to subscribe
    - **subscription_type**: Type of content (default: ALL)
    - **frequency**: Email frequency (default: WEEKLY)
    
    **Response:**
    - Subscription details
    - Confirmation email will be sent
    """
    subscription = await SubscriptionService.create_subscription(
        db=db,
        email=subscription_data.email,
        subscription_type=subscription_data.subscription_type,
        frequency=subscription_data.frequency
    )
    
    return SubscriptionResponse.model_validate(subscription)


@router.get("/confirm/{token}", response_class=HTMLResponse)
async def confirm_subscription(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm email subscription
    
    **Public endpoint** - Accessed via email link
    
    **Path Parameters:**
    - **token**: Confirmation token from email
    
    **Response:**
    - HTML page confirming subscription
    """
    subscription = await SubscriptionService.confirm_subscription(db, token)
    
    # Return HTML confirmation page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>订阅确认成功</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                padding: 48px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            .success-icon {{
                width: 80px;
                height: 80px;
                background: #10b981;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 24px;
            }}
            .checkmark {{
                width: 40px;
                height: 40px;
                border: 4px solid white;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
                margin-top: 10px;
            }}
            h1 {{
                color: #1f2937;
                margin: 0 0 16px;
                font-size: 28px;
            }}
            p {{
                color: #6b7280;
                line-height: 1.6;
                margin: 0 0 32px;
            }}
            .email {{
                background: #f3f4f6;
                padding: 12px 20px;
                border-radius: 8px;
                color: #4b5563;
                font-weight: 500;
                margin-bottom: 24px;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 32px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: transform 0.2s;
            }}
            .button:hover {{
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">
                <div class="checkmark"></div>
            </div>
            <h1>订阅确认成功！</h1>
            <p>感谢您订阅我们的内容更新</p>
            <div class="email">{subscription.email}</div>
            <p>您将会收到 <strong>{subscription.subscription_type.value}</strong> 类型的内容，频率为 <strong>{subscription.frequency.value}</strong></p>
            <a href="/" class="button">返回首页</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/unsubscribe/{token}", response_class=HTMLResponse)
async def unsubscribe(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Unsubscribe from emails
    
    **Public endpoint** - Accessed via email link
    
    **Path Parameters:**
    - **token**: Unsubscribe token from email
    
    **Response:**
    - HTML page confirming unsubscription
    """
    subscription = await SubscriptionService.unsubscribe(db, token)
    
    # Return HTML confirmation page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>退订成功</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                padding: 48px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            h1 {{
                color: #1f2937;
                margin: 0 0 16px;
                font-size: 28px;
            }}
            p {{
                color: #6b7280;
                line-height: 1.6;
                margin: 0 0 24px;
            }}
            .email {{
                background: #f3f4f6;
                padding: 12px 20px;
                border-radius: 8px;
                color: #4b5563;
                font-weight: 500;
                margin-bottom: 24px;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 14px 32px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: transform 0.2s;
            }}
            .button:hover {{
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>退订成功</h1>
            <p>您已成功退订我们的邮件列表</p>
            <div class="email">{subscription.email}</div>
            <p>如果这是误操作，您可以随时重新订阅</p>
            <a href="/" class="button">返回首页</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


# ============================================================================
# Admin Endpoints
# ============================================================================

@router.get("", response_model=SubscriptionListResponse)
async def get_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[SubscriptionStatus] = None,
    subscription_type: Optional[SubscriptionType] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all subscriptions (Admin only)
    
    **Query Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records (default: 100, max: 1000)
    - **status**: Filter by status (PENDING/ACTIVE/UNSUBSCRIBED)
    - **subscription_type**: Filter by type
    
    **Response:**
    - List of subscriptions with pagination info
    """
    subscriptions = await SubscriptionService.get_subscriptions(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        subscription_type=subscription_type
    )

    # Calculate page number from skip and limit
    page = (skip // limit) + 1 if limit > 0 else 1

    return SubscriptionListResponse(
        items=[SubscriptionResponse.model_validate(s) for s in subscriptions],
        total=len(subscriptions),
        page=page,
        page_size=limit
    )


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    update_data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update subscription (Admin only)
    
    **Path Parameters:**
    - **subscription_id**: Subscription ID
    
    **Request Body:**
    - **subscription_type**: New subscription type (optional)
    - **frequency**: New frequency (optional)
    - **status**: New status (optional)
    """
    subscription = await SubscriptionService.update_subscription(
        db=db,
        subscription_id=subscription_id,
        subscription_type=update_data.subscription_type,
        frequency=update_data.frequency,
        status=update_data.status
    )
    
    return SubscriptionResponse.model_validate(subscription)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete subscription (Admin only)
    
    **Path Parameters:**
    - **subscription_id**: Subscription ID
    """
    await SubscriptionService.delete_subscription(db, subscription_id)
    return None

