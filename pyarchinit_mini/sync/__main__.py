import argparse, logging, sys
from .config import load_config
from .runner import run

def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m pyarchinit_mini.sync",
                                description="Sync classic pyarchinit -> pyarchinit_v2")
    p.add_argument("--config", default=None)
    p.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    p.add_argument("--tables", default=None, help="comma-separated subset")
    p.add_argument("--log", default=None, help="log file (default: stderr)")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, filename=args.log,
                        format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config(args.config)
    tables = [t.strip() for t in args.tables.split(",")] if args.tables else None
    results = run(cfg, tables=tables, dry_run=not args.apply)
    errors = [r for r in results if r.error]
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
