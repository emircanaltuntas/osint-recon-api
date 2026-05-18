import os
import asyncio
import logging
import maigret
from typing import Dict, Any, Optional, List
from maigret.checking import maigret as maigret_check
from maigret.sites import MaigretDatabase
from maigret.notify import QueryNotifyPrint

class MaigretScraper:
    def __init__(self):
        self.db = None
        self.sites = {}
        self._lock = asyncio.Lock()

    async def load(self):
        if self.db:
            return

        async with self._lock:
            if self.db:
                return
            try:
                base_path = os.path.dirname(maigret.__file__)
                db_path = os.path.join(base_path, 'resources', 'data.json')

                self.db = MaigretDatabase()
                self.db.load_from_path(db_path)

                rank_list = self.db.ranked_sites_dict(top=150)
                self.sites = dict(rank_list)

            except Exception as e:
                self.sites = {}

    async def search(self, username: str) -> Dict[str, Any]:
        await self.load()

        if not self.sites:
            return {
                "query": username,
                "found_accounts": [],
                "error": "Site DB load failed"
            }

        logger = logging.getLogger('maigret')
        logger.setLevel(logging.CRITICAL)

        notify = QueryNotifyPrint(
            result=None,
            verbose=False,
            print_found_only=True,
            skip_check_errors=True,
            color=False
        )

        try:
            results = await maigret_check(
                username=username,
                site_dict=self.sites,
                query_notify=notify,
                logger=logger,
                timeout=5,
                max_connections=50,
                no_progressbar=True,
                id_type='username',
                is_parsing_enabled=False
            )

            found_sites = []
            for site_name, res in results.items():
                if res.get("status") and res.get("status").is_found():
                    found_sites.append(site_name)

            return {
                "query": username,
                "found_accounts": found_sites,
                "scanned_count": len(self.sites)
            }

        except Exception as e:
            return {
                "query": username,
                "found_accounts": [],
                "error": str(e)
            }

scraper = MaigretScraper()

async def fetch_username_data(username: str) -> Optional[Dict[str, Any]]:
    data = await scraper.search(username)
    return data
