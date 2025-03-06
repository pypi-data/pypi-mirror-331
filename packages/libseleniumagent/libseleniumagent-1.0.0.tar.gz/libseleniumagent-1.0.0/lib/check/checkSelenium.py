import time
import os
from libseleniumagent.version import __version__ as libseleniumagent_version
from pylibagent.check import CheckBase
from selenium import webdriver
from selenium import __version__ as selenium_version
from selenium.webdriver.chrome.options import Options
from typing import Dict, List, Any
from ..tests import TESTS
from ..version import __version__ as version


class CheckSelenium(CheckBase):
    key = 'selenium'
    interval = int(os.getenv('CHECK_INTERVAL', '300'))

    @classmethod
    async def run(cls) -> Dict[str, List[Dict[str, Any]]]:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=chrome_options)

        items = []
        for test in TESTS:
            t0 = time.time()
            success = True
            error = None
            try:
                driver.get(test.url)
                test.test(driver)
            except Exception as e:
                success = False
                error = str(e) or type(e).__name__
            items.append({
                'name': test.name,
                'url': test.url,
                'success': success,
                'error': error,
                'duration': time.time() - t0,
                'description': test.description,
                'version': test.version,
            })

        driver.quit()

        total = {
            'name': 'total',
            'success_count': sum(i['success'] for i in items),
            'failed_count': sum(not i['success'] for i in items),
            'num_checks': len(items),
            'total_duration': sum(i['duration'] for i in items),
        }
        agent = {
            'name': 'agent',
            'libseleniumagent_version': libseleniumagent_version,
            'selenium_version': selenium_version,
            'version': version,
        }
        state = {'tests': items, 'total': [total], 'agent': [agent]}
        return state
