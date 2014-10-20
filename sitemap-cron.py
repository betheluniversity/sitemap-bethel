__author__ = 'ejc84332'

#python
import time
import logging

#ext
import crython
#local
import sitemap
import config

# @crython.job(second=range(0,60,10))
# def foo():
#     with open('/var/www/staging/public/_testing/jmo/cron.txt', 'a') as f:
#         f.write("%s -- Print info every 10 seconds to test supervisord\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
#         print 'test'


@crython.job(expr='@daily')
def sitemap_cron():
    sitemap.sitemap()
    logging.info("sitemap done")
    print "sitemap done"
    ##Now that sitemap is done generating take care of a few things.
    ##1. fix up robots.txt and site-index.xml (remove system-region)
    #robots.txt and sitemap-index.xml published at midnight,
    with open(config.ROBOTS_FILE) as file:
        lines = file.read().splitlines()
        ##The last 3 lines are the XML stuff we don't want. so get rid of them
        lines = lines[:-3]

    with open(config.ROBOTS_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))

    ##Now sitemap-index.xml
    with open(config.SITEMAP_INDEX_FILE) as file:
        lines = file.read().splitlines()
        ##The last 3 lines are the XML stuff we don't want. so get rid of them
        lines = lines[:-3]
        ##the first line is blank so get rid of it
        lines = lines[1:]

    ##2. Move the new sitemap to replace the old one. Can't replace the old one right away
    ## because it is a generator, so it would be incomplete while it runs.
    with open(config.SITEMAP_INDEX_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))

    with open(config.SITEMAP_FILE) as file:
        lines = file.read().splitlines()

    with open(config.SITEMAP_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))


if __name__ == '__main__':
    crython.tab.start()
    while True:
        ##If you put Python to sleep crthon will still run.
        ##Wake up every minute anyway?
        time.sleep(60)