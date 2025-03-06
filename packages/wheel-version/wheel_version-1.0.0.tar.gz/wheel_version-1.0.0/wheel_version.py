# /// script
# dependencies = ["packaging"]
# ///
import argparse
import json
import os

from packaging.utils import InvalidWheelFilename, parse_wheel_filename


def main() -> None:
    p = argparse.ArgumentParser()
    pg = p.add_mutually_exclusive_group()
    pg.add_argument('-d', '--dev', action='store_true')
    pg.add_argument('-p', '--pre', action='store_true')
    pg.add_argument('-j', '--json', action='store_true')
    p.add_argument('filename', metavar='PATH', type=os.path.basename)
    args = p.parse_args()

    try:
        version = parse_wheel_filename(args.filename)[1]
    except InvalidWheelFilename as e:
        raise SystemExit(e) from None

    if args.dev:
        raise SystemExit(not version.is_devrelease)

    if args.pre:
        raise SystemExit(not version.is_prerelease)

    if args.json:
        print(json.dumps({k: getattr(version, k) for k in dir(version) if k[0] != '_'}))
        return

    print(version)


if __name__ == '__main__':
    main()
