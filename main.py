import argparse
from datetime import datetime
import dateutil.parser
from getpass import getpass

import neveo.utils as utils
from neveo.neveo_endpoint import NeveoEndpoint
from neveo.download import download


def process_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument("--action", default="list", help="action")
    parser.add_argument("--password", help="neveo password]")
    parser.add_argument("--login", help="neveo login")
    parser.add_argument("--limit", help="limit")
    return parser.parse_args()


def main():
    start = datetime.now()
    parser = argparse.ArgumentParser()
    args = process_args(parser)
    login = args.login if args.login else input("Email: ")
    password = args.password if args.password else getpass("Password: ")
    action = args.action

    neveo_endpoint = NeveoEndpoint(
        url="https://neveo.io", login=login, password=password
    )

    logger.debug("login : {}".format(login))
    if action == "list":
        page = 1
        while True:
            medias = neveo_endpoint.list_medias(page=page)
            page += 1
            if page > 100:
                break
            if len(medias) == 0:
                break
            for media in medias:
                logger.info(
                    "media name {}, {}. {}".format(
                        media.get("id"), media.get("created_at"), media.get("original")
                    )
                )
                media_date = dateutil.parser.isoparse(media.get("created_at"))
                if media_date > dateutil.parser.isoparse("2021-01-01T00:00:00.000Z"):
                    name = "{}.jpeg".format(media.get("id"))
                    download(name=name, url=media.get("original"))

        delta = datetime.now() - start
        logger.info("extract media done in {} sec".format(delta.seconds))


logger = utils.get_logger(__name__)
if __name__ == "__main__":
    # execute only if run as a script
    main()
