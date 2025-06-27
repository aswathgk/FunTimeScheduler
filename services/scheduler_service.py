"""
Scheduler service for FunTime Scheduler.
Manages APScheduler jobs for website blocking/unblocking.
"""

import logging
from datetime import datetime, time
from typing import Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore

logger = logging.getLogger(__name__)

class SchedulerService:
    """Manages scheduled website blocking/unblocking."""
    
    def __init__(self, database_manager, adguard_api):
        """Initialize scheduler service."""
        self.db_manager = database_manager
        self.adguard_api = adguard_api
        
        # Configure scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=2)
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 30
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'  # Use UTC for consistency
        )
        
        self._running = False
        logger.info("Scheduler service initialized")
    
    def start(self):
        """Start the scheduler and load existing schedules."""
        try:
            if not self._running:
                self.scheduler.start()
                self._running = True
                logger.info("Scheduler started")
                
                # Load existing enabled websites
                self._load_existing_schedules()
            else:
                logger.warning("Scheduler is already running")
                
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler."""
        try:
            if self._running:
                self.scheduler.shutdown(wait=False)
                self._running = False
                logger.info("Scheduler stopped")
            else:
                logger.warning("Scheduler is not running")
                
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running and self.scheduler.running
    
    def _load_existing_schedules(self):
        """Load and schedule all enabled websites from database."""
        try:
            websites = self.db_manager.get_enabled_websites()
            for website in websites:
                self.schedule_website(
                    website['id'],
                    website['url'],
                    website['start_time'],
                    website['end_time']
                )
            logger.info(f"Loaded {len(websites)} existing schedules")
            
        except Exception as e:
            logger.error(f"Error loading existing schedules: {e}")
    
    def schedule_website(self, website_id: int, url: str, start_time: str, end_time: str):
        """Schedule blocking and unblocking for a website."""
        try:
            # Parse time strings (expected format: HH:MM)
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            # Create job IDs
            block_job_id = f"block_{website_id}"
            unblock_job_id = f"unblock_{website_id}"
            
            # Remove existing jobs if they exist
            self.remove_website_schedule(website_id)
            
            # Schedule blocking job
            self.scheduler.add_job(
                func=self._block_website,
                trigger=CronTrigger(hour=start_hour, minute=start_minute),
                args=[website_id, url],
                id=block_job_id,
                name=f"Block {url}",
                replace_existing=True
            )
            
            # Schedule unblocking job
            self.scheduler.add_job(
                func=self._unblock_website,
                trigger=CronTrigger(hour=end_hour, minute=end_minute),
                args=[website_id, url],
                id=unblock_job_id,
                name=f"Unblock {url}",
                replace_existing=True
            )
            
            logger.info(f"Scheduled {url}: block at {start_time}, unblock at {end_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling website {url}: {e}")
            raise
    
    def remove_website_schedule(self, website_id: int):
        """Remove all scheduled jobs for a website."""
        try:
            block_job_id = f"block_{website_id}"
            unblock_job_id = f"unblock_{website_id}"
            
            # Remove jobs if they exist
            for job_id in [block_job_id, unblock_job_id]:
                try:
                    self.scheduler.remove_job(job_id)
                    logger.debug(f"Removed job: {job_id}")
                except Exception:
                    # Job doesn't exist, ignore
                    pass
            
            logger.info(f"Removed schedule for website ID: {website_id}")
            
        except Exception as e:
            logger.error(f"Error removing schedule for website {website_id}: {e}")
    
    def _block_website(self, website_id: int, url: str):
        """Block a website (called by scheduler)."""
        try:
            logger.info(f"Attempting to block website: {url}")
            
            success = self.adguard_api.block_domain(url)
            
            # Log the action
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='block',
                success=success,
                error_message=None if success else "Failed to block domain"
            )
            
            if success:
                logger.info(f"Successfully blocked website: {url}")
            else:
                logger.error(f"Failed to block website: {url}")
                
        except Exception as e:
            error_msg = f"Error blocking website {url}: {e}"
            logger.error(error_msg)
            
            # Log the error
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='block',
                success=False,
                error_message=str(e)
            )
    
    def _unblock_website(self, website_id: int, url: str):
        """Unblock a website (called by scheduler)."""
        try:
            logger.info(f"Attempting to unblock website: {url}")
            
            success = self.adguard_api.unblock_domain(url)
            
            # Log the action
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='unblock',
                success=success,
                error_message=None if success else "Failed to unblock domain"
            )
            
            if success:
                logger.info(f"Successfully unblocked website: {url}")
            else:
                logger.error(f"Failed to unblock website: {url}")
                
        except Exception as e:
            error_msg = f"Error unblocking website {url}: {e}"
            logger.error(error_msg)
            
            # Log the error
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='unblock',
                success=False,
                error_message=str(e)
            )
    
    def get_scheduled_jobs(self) -> list:
        """Get list of currently scheduled jobs."""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting scheduled jobs: {e}")
            return []
    
    def force_block_website(self, website_id: int, url: str) -> bool:
        """Manually block a website immediately."""
        try:
            logger.info(f"Force blocking website: {url}")
            success = self.adguard_api.block_domain(url)
            
            # Log the action
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='manual_block',
                success=success,
                error_message=None if success else "Failed to block domain"
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error force blocking website {url}: {e}")
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='manual_block',
                success=False,
                error_message=str(e)
            )
            return False
    
    def force_unblock_website(self, website_id: int, url: str) -> bool:
        """Manually unblock a website immediately."""
        try:
            logger.info(f"Force unblocking website: {url}")
            success = self.adguard_api.unblock_domain(url)
            
            # Log the action
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='manual_unblock',
                success=success,
                error_message=None if success else "Failed to unblock domain"
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error force unblocking website {url}: {e}")
            self.db_manager.log_action(
                website_id=website_id,
                website_url=url,
                action='manual_unblock',
                success=False,
                error_message=str(e)
            )
            return False
