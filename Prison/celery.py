from celery.schedules import crontab

app.conf.beat_schedule = {
    'expire-pending-prisoners-every-hour': {
        'task': 'Prison.Request_Expiration.expire_pending_prisoners',
        'schedule': crontab(minute=0, hour='*'),
    },
}
