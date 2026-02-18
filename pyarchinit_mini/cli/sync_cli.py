# -*- coding: utf-8 -*-
"""CLI sync commands for StratiGraph integration."""
import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.option('--config-dir', type=click.Path(), default=None, help='Config directory')
@click.pass_context
def sync(ctx, config_dir):
    """StratiGraph sync commands."""
    ctx.ensure_object(dict)
    ctx.obj['config_dir'] = config_dir


@sync.command()
@click.pass_context
def status(ctx):
    """Show sync status."""
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator(config_dir=ctx.obj.get('config_dir'))
    s = orch.get_status()
    console.print(f"State: [bold]{s['state']}[/bold]")
    console.print(f"Online: {'[green]Yes[/green]' if s['online'] else '[red]No[/red]'}")
    console.print(f"Running: {s['running']}")
    stats = s.get('queue_stats', {})
    if stats:
        console.print(
            f"Queue -- pending: {stats.get('pending', 0)}, "
            f"completed: {stats.get('completed', 0)}, "
            f"failed: {stats.get('failed', 0)}"
        )


@sync.command()
@click.option('--site', '-s', default=None, help='Site name to export')
@click.pass_context
def export(ctx, site):
    """Export a StratiGraph bundle."""
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator(config_dir=ctx.obj.get('config_dir'))
    result = orch.export_bundle(site_name=site)
    if result['success']:
        console.print(f"[green]Bundle exported: {result['bundle_path']}[/green]")
    else:
        console.print(f"[red]Export failed: {', '.join(result['errors'])}[/red]")


@sync.command()
@click.pass_context
def push(ctx):
    """Push pending bundles to server."""
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator(config_dir=ctx.obj.get('config_dir'))
    orch.sync_now()
    console.print("[green]Sync triggered[/green]")


@sync.command()
@click.option('--endpoint', '-e', default=None, help='Server URL to set')
@click.pass_context
def config(ctx, endpoint):
    """View or set sync configuration."""
    from pyarchinit_mini.stratigraph.sync_state_machine import SettingsManager
    sm = SettingsManager()
    if endpoint:
        sm.set('upload_endpoint', endpoint)
        console.print(f"[green]Endpoint set: {endpoint}[/green]")
    else:
        ep = sm.get('upload_endpoint', 'http://localhost:8080/api/v1/bundles')
        console.print(f"Upload endpoint: {ep}")


# Queue subgroup
@sync.group()
@click.pass_context
def queue(ctx):
    """Manage the sync queue."""
    pass


@queue.command('list')
@click.pass_context
def queue_list(ctx):
    """List queue entries."""
    from pyarchinit_mini.stratigraph import SyncQueue
    config_dir = ctx.obj.get('config_dir')
    db_path = None
    if config_dir:
        import os
        db_path = os.path.join(config_dir, "stratigraph_sync_queue.sqlite")
    q = SyncQueue(db_path=db_path)
    entries = q.get_all()
    table = Table(title="Sync Queue")
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Bundle")
    table.add_column("Attempts")
    for e in entries:
        table.add_row(str(e.id), e.status, e.bundle_path, str(e.attempts))
    console.print(table)


@queue.command('retry')
@click.argument('entry_id', type=int)
@click.pass_context
def queue_retry(ctx, entry_id):
    """Retry a failed queue entry by ID."""
    from pyarchinit_mini.stratigraph import SyncQueue
    config_dir = ctx.obj.get('config_dir')
    db_path = None
    if config_dir:
        import os
        db_path = os.path.join(config_dir, "stratigraph_sync_queue.sqlite")
    q = SyncQueue(db_path=db_path)
    q.retry_failed(entry_id)
    console.print(f"[green]Entry {entry_id} re-queued[/green]")


@queue.command('clean')
@click.option('--older-than', type=int, default=7, help='Remove completed entries older than N days')
@click.pass_context
def queue_clean(ctx, older_than):
    """Remove completed queue entries."""
    from pyarchinit_mini.stratigraph import SyncQueue
    config_dir = ctx.obj.get('config_dir')
    db_path = None
    if config_dir:
        import os
        db_path = os.path.join(config_dir, "stratigraph_sync_queue.sqlite")
    q = SyncQueue(db_path=db_path)
    q.cleanup_completed(older_than_days=older_than)
    console.print(f"[green]Cleaned completed entries older than {older_than} days[/green]")
