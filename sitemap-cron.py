# python
import time
import logging
import requests

# ext
import crython

# local
import sitemap
import config
from raven import Client


# @crython.job(second=range(0,60,10))
# def foo():
#     with open('/var/www/staging/public/_testing/jmo/cron.txt', 'a') as f:
#         f.write("%s -- Print info every 10 seconds to test supervisord\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
#         print 'test'


client = Client(config.SENTRY_URL)


@crython.job(expr='@daily')
def sitemap_cron():
    sitemap.sitemap()
    logging.info("sitemap done")
    # Now that sitemap is done generating take care of a few things.
    # 1. fix up robots.txt and site-index.xml (remove system-region)
    # robots.txt and sitemap-index.xml published at midnight,
    with open(config.ROBOTS_FILE) as file:
        lines = file.read().splitlines()

    with open(config.ROBOTS_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))

    # Now sitemap-index.xml
    with open(config.SITEMAP_INDEX_FILE) as file:
        lines = file.read().splitlines()

    # 2. Move the new sitemap to replace the old one. Can't replace the old one right away
    # because it is a generator, so it would be incomplete while it runs.
    with open(config.SITEMAP_INDEX_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))

    with open(config.SITEMAP_FILE) as file:
        lines = file.read().splitlines()

    with open(config.SITEMAP_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))


@crython.job(expr='@daily')
def get_adult_programs():
    r = requests.get("http://programs.bethel.edu/adultprograms")
    print "got %s" % r.text

if __name__ == '__main__':
    crython.tab.start()
    while True:
        # If you put Python to sleep crthon will still run.
        # Wake up every minute anyway?
        time.sleep(60)
