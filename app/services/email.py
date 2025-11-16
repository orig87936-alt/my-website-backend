"""
Email notification service using Resend API
"""
import asyncio
from typing import Optional
from datetime import datetime
import httpx

from app.config import get_settings

settings = get_settings()


class EmailService:
    """Service for sending emails via Resend API"""
    
    RESEND_API_URL = "https://api.resend.com/emails"
    
    @staticmethod
    async def send_appointment_confirmation(
        to_email: str,
        name: str,
        confirmation_number: str,
        appointment_date: str,
        time_slot: str,
        service_type: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        发送预约确认邮件
        
        Args:
            to_email: Recipient email address
            name: Recipient name
            confirmation_number: Appointment confirmation number
            appointment_date: Appointment date
            time_slot: Appointment time slot
            service_type: Service type (optional)
            notes: Additional notes (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # 如果没有配置 Resend API key，跳过发送（开发环境）
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "your-resend-api-key-here":
            print(f"⚠️  邮件服务未配置，跳过发送邮件到 {to_email}")
            print(f"   预约确认号: {confirmation_number}")
            print(f"   预约时间: {appointment_date} {time_slot}")
            return True  # 返回成功，避免阻塞预约流程
        
        # 构建邮件内容
        subject = f"预约确认 - {confirmation_number}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 30px; }}
                .info-row {{ margin: 15px 0; }}
                .label {{ font-weight: bold; color: #6B7280; }}
                .value {{ color: #111827; }}
                .footer {{ text-align: center; padding: 20px; color: #6B7280; font-size: 14px; }}
                .confirmation-number {{ font-size: 24px; font-weight: bold; color: #4F46E5; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>预约确认</h1>
                </div>
                <div class="content">
                    <p>尊敬的 {name}，</p>
                    <p>您的预约已成功提交！以下是您的预约详情：</p>
                    
                    <div class="info-row">
                        <span class="label">确认号：</span>
                        <span class="confirmation-number">{confirmation_number}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="label">预约日期：</span>
                        <span class="value">{appointment_date}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="label">预约时间：</span>
                        <span class="value">{time_slot}</span>
                    </div>
                    
                    {f'<div class="info-row"><span class="label">服务类型：</span><span class="value">{service_type}</span></div>' if service_type else ''}
                    
                    {f'<div class="info-row"><span class="label">备注：</span><span class="value">{notes}</span></div>' if notes else ''}
                    
                    <p style="margin-top: 30px;">
                        如需取消或修改预约，请联系我们的客服团队。
                    </p>
                    
                    <p>感谢您的预约！</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿直接回复。</p>
                    <p>&copy; {datetime.now().year} 新闻平台. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        预约确认
        
        尊敬的 {name}，
        
        您的预约已成功提交！以下是您的预约详情：
        
        确认号：{confirmation_number}
        预约日期：{appointment_date}
        预约时间：{time_slot}
        {'服务类型：' + service_type if service_type else ''}
        {'备注：' + notes if notes else ''}
        
        如需取消或修改预约，请联系我们的客服团队。
        
        感谢您的预约！
        
        ---
        此邮件由系统自动发送，请勿直接回复。
        © {datetime.now().year} 新闻平台. All rights reserved.
        """
        
        # 发送邮件
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    EmailService.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": settings.EMAIL_FROM,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                        "text": text_content
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"✅ 邮件发送成功: {to_email}")
                    return True
                else:
                    print(f"❌ 邮件发送失败: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 邮件发送异常: {str(e)}")
            return False
    
    @staticmethod
    async def send_appointment_reminder(
        to_email: str,
        name: str,
        confirmation_number: str,
        appointment_date: str,
        time_slot: str
    ) -> bool:
        """
        发送预约提醒邮件（提前1天）
        
        Args:
            to_email: Recipient email address
            name: Recipient name
            confirmation_number: Appointment confirmation number
            appointment_date: Appointment date
            time_slot: Appointment time slot
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # 如果没有配置 Resend API key，跳过发送
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "your-resend-api-key-here":
            print(f"⚠️  邮件服务未配置，跳过发送提醒邮件到 {to_email}")
            return True
        
        subject = f"预约提醒 - {confirmation_number}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #F59E0B; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 30px; }}
                .reminder {{ background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ 预约提醒</h1>
                </div>
                <div class="content">
                    <p>尊敬的 {name}，</p>
                    
                    <div class="reminder">
                        <p><strong>您的预约即将到来！</strong></p>
                        <p>预约时间：{appointment_date} {time_slot}</p>
                        <p>确认号：{confirmation_number}</p>
                    </div>
                    
                    <p>请准时到达。如需取消或修改，请尽快联系我们。</p>
                    
                    <p>期待与您见面！</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    EmailService.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": settings.EMAIL_FROM,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content
                    },
                    timeout=10.0
                )
                
                return response.status_code == 200
                    
        except Exception as e:
            print(f"❌ 提醒邮件发送异常: {str(e)}")
            return False

    @staticmethod
    async def send_verification_code(
        to_email: str,
        code: str,
        purpose: str = "register"
    ) -> bool:
        """
        Send verification code email

        Args:
            to_email: Recipient email address
            code: 6-digit verification code
            purpose: Verification purpose (register/reset/change)

        Returns:
            True if email sent successfully, False otherwise
        """
        # Purpose-specific content
        purpose_titles = {
            "register": "注册验证码",
            "reset": "密码重置验证码",
            "change": "邮箱变更验证码"
        }

        purpose_messages = {
            "register": "感谢您注册我们的平台！",
            "reset": "您正在重置密码。",
            "change": "您正在更改邮箱地址。"
        }

        title = purpose_titles.get(purpose, "验证码")
        message = purpose_messages.get(purpose, "")

        # If no API key configured, print to console (development)
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "your-resend-api-key-here":
            print(f"⚠️  邮件服务未配置，验证码: {code} (发送到 {to_email})")
            return True

        subject = f"{title} - {code}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 30px; }}
                .code-box {{ background-color: #EEF2FF; border: 2px dashed #4F46E5; padding: 20px; text-align: center; margin: 20px 0; }}
                .code {{ font-size: 32px; font-weight: bold; color: #4F46E5; letter-spacing: 8px; }}
                .warning {{ background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6B7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    <p>{message}</p>
                    <p>您的验证码是：</p>

                    <div class="code-box">
                        <div class="code">{code}</div>
                    </div>

                    <div class="warning">
                        <p><strong>⚠️ 重要提示：</strong></p>
                        <ul>
                            <li>验证码有效期为 <strong>10 分钟</strong></li>
                            <li>请勿将验证码告诉他人</li>
                            <li>如非本人操作，请忽略此邮件</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿直接回复。</p>
                    <p>&copy; {datetime.now().year} 新闻平台. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        {title}

        {message}

        您的验证码是：{code}

        重要提示：
        - 验证码有效期为 10 分钟
        - 请勿将验证码告诉他人
        - 如非本人操作，请忽略此邮件

        ---
        此邮件由系统自动发送，请勿直接回复。
        © {datetime.now().year} 新闻平台. All rights reserved.
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    EmailService.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": settings.EMAIL_FROM,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                        "text": text_content
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    print(f"✅ 验证码邮件发送成功: {to_email}")
                    return True
                else:
                    print(f"❌ 验证码邮件发送失败: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"❌ 验证码邮件发送异常: {str(e)}")
            return False

    @staticmethod
    async def send_subscription_confirmation(
        to_email: str,
        confirmation_token: str
    ) -> bool:
        """
        发送订阅确认邮件

        Args:
            to_email: Recipient email address
            confirmation_token: Confirmation token

        Returns:
            True if email sent successfully, False otherwise
        """
        # 如果没有配置 Resend API key，跳过发送（开发环境）
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "your-resend-api-key-here":
            print(f"⚠️  邮件服务未配置，跳过发送订阅确认邮件到 {to_email}")
            print(f"   确认链接: http://localhost:8000/api/v1/subscriptions/confirm/{confirmation_token}")
            return True

        # 构建确认链接
        confirmation_url = f"http://localhost:8000/api/v1/subscriptions/confirm/{confirmation_token}"

        subject = "确认您的订阅"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 30px; }}
                .button {{ display: inline-block; background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6B7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>确认您的订阅</h1>
                </div>
                <div class="content">
                    <p>感谢您订阅我们的内容更新！</p>
                    <p>请点击下面的按钮确认您的订阅：</p>
                    <div style="text-align: center;">
                        <a href="{confirmation_url}" class="button">确认订阅</a>
                    </div>
                    <p style="margin-top: 30px; font-size: 14px; color: #6B7280;">
                        如果按钮无法点击，请复制以下链接到浏览器：<br>
                        {confirmation_url}
                    </p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    EmailService.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAIL_FROM,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    print(f"✅ 订阅确认邮件已发送到 {to_email}")
                    return True
                else:
                    print(f"❌ 发送订阅确认邮件失败: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"❌ 发送订阅确认邮件失败: {str(e)}")
            return False

    @staticmethod
    async def send_subscription_welcome(
        to_email: str,
        subscription_type: str
    ) -> bool:
        """
        发送订阅欢迎邮件

        Args:
            to_email: Recipient email address
            subscription_type: Type of subscription

        Returns:
            True if email sent successfully, False otherwise
        """
        # 如果没有配置 Resend API key，跳过发送（开发环境）
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "your-resend-api-key-here":
            print(f"⚠️  邮件服务未配置，跳过发送欢迎邮件到 {to_email}")
            return True

        subject = "欢迎订阅！"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 30px; }}
                .footer {{ text-align: center; padding: 20px; color: #6B7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>欢迎订阅！</h1>
                </div>
                <div class="content">
                    <p>您的订阅已成功激活！</p>
                    <p>您订阅的内容类型：<strong>{subscription_type}</strong></p>
                    <p>我们会定期向您发送最新的内容更新。</p>
                    <p>感谢您的支持！</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    EmailService.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAIL_FROM,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    print(f"✅ 欢迎邮件已发送到 {to_email}")
                    return True
                else:
                    print(f"❌ 发送欢迎邮件失败: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"❌ 发送欢迎邮件失败: {str(e)}")
            return False

