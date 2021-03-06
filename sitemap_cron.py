# local
import sys
import sitemap
import config
import sentry_sdk
from github_connection import GH
from xml.sax.handler import ContentHandler
from xml.sax import make_parser


if config.SENTRY_URL:
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(dsn=config.SENTRY_URL, integrations=[FlaskIntegration()])


# This method just parses the file to check for syntax errors
# It doesn't return something, since if an exception occurs,
# it is caught in a try, except and sent out via sentry
def parse_file(filename):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(filename)


def sitemap_cron():
    gh = GH(config.GH_LOGIN)
    txt = gh.get_humans_text()

    with open(config.HUMANS_PRODUCTION_FILE, "w") as text_file:
        text_file.write(txt)

    # 1. fix up robots.txt and site-index.xml (remove system-region)
    # robots.txt and sitemap-index.xml published at midnight,
    with open(config.ROBOTS_FILE) as file:
        lines = file.read().splitlines()
    with open(config.ROBOTS_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))

    try:
        sitemap.sitemap()
    except:
        sentry_sdk.capture_exception()

    # 2. Move the new sitemap to replace the old one. Can't replace the old one right away
    # because it is a generator, so it would be incomplete while it runs.
    with open(config.SITEMAP_FILE) as file:
        lines = file.read().splitlines()
    with open(config.SITEMAP_FILE) as file:
        try:
            parse_file(file)
        except Exception as e:
            # Throws an error and exits so file isn't written to with invalid xml
            sentry_sdk.capture_message(repr(e))
            sys.exit(0)
    with open(config.SITEMAP_PRODUCTION_FILE, 'w') as file:
        file.write("\n".join(lines))


# This is used by cron to create the sitemap
sitemap_cron()