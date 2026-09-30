from datetime import timedelta
from . import config, repository as repo
from .cwa_client import fetch_forecasts, CWAError

def get_forecast(location, force=False):
    """回傳 (rows, fetched_at, status, message)；status: fresh / cache / stale / empty"""
    last = repo.last_fetch()
    if last and not force and repo.now() - last < timedelta(minutes=config.CACHE_MINUTES):
        rows = repo.load(location)
        if rows:
            return rows, last, "cache", ""
    try:
        repo.save(fetch_forecasts())
        return repo.load(location), repo.last_fetch(), "fresh", ""
    except CWAError as e:
        rows = repo.load(location)
        return rows, repo.last_fetch(), ("stale" if rows else "empty"), str(e)
