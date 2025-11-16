"""
T069: Background task scheduler for periodic maintenance tasks
"""
import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services.translation import TranslationService


class TaskScheduler:
    """Background task scheduler for periodic maintenance"""
    
    def __init__(self):
        self.running = False
        self.tasks: list[asyncio.Task] = []
    
    async def cleanup_translation_cache_task(self):
        """
        T069: Periodic task to clean up expired translation cache
        Runs daily at 2 AM UTC
        """
        while self.running:
            try:
                # Calculate time until next 2 AM UTC
                now = datetime.utcnow()
                next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
                
                # If it's already past 2 AM today, schedule for tomorrow
                if now.hour >= 2:
                    from datetime import timedelta
                    next_run = next_run + timedelta(days=1)
                
                # Calculate sleep duration
                sleep_seconds = (next_run - now).total_seconds()
                
                print(f"🕐 Next cache cleanup scheduled at {next_run} UTC ({sleep_seconds/3600:.1f} hours)")
                
                # Wait until next run time
                await asyncio.sleep(sleep_seconds)
                
                # Execute cleanup
                print(f"🧹 Starting translation cache cleanup at {datetime.utcnow()}")
                
                async with AsyncSessionLocal() as db:
                    translation_service = TranslationService(db)
                    deleted_count = await translation_service.cleanup_expired_cache(days=30)
                    
                    # Get statistics after cleanup
                    stats = await translation_service.get_cache_statistics()
                    
                    print(f"✅ Cache cleanup completed:")
                    print(f"   - Deleted: {deleted_count} entries")
                    print(f"   - Remaining: {stats['total_cache_entries']} entries")
                    print(f"   - Cache hit rate: {stats['cache_hit_rate']:.2f}%")
                
            except Exception as e:
                print(f"⚠️  Error in cache cleanup task: {e}")
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)
    
    async def start(self):
        """Start all background tasks"""
        if self.running:
            print("⚠️  Task scheduler already running")
            return
        
        self.running = True
        print("🚀 Starting background task scheduler...")
        
        # Start cache cleanup task
        cleanup_task = asyncio.create_task(self.cleanup_translation_cache_task())
        self.tasks.append(cleanup_task)
        
        print("✅ Background tasks started")
    
    async def stop(self):
        """Stop all background tasks"""
        if not self.running:
            return
        
        print("🛑 Stopping background task scheduler...")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        print("✅ Background tasks stopped")


# Global scheduler instance
scheduler = TaskScheduler()

