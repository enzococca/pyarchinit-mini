# -*- coding: utf-8 -*-
"""Test CLI sync commands."""
import os
import tempfile

from click.testing import CliRunner
from pyarchinit_mini.cli.sync_cli import sync


def test_sync_group_help():
    runner = CliRunner()
    result = runner.invoke(sync, ['--help'])
    assert result.exit_code == 0
    assert 'StratiGraph sync commands' in result.output


def test_status_command_runs():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as td:
        result = runner.invoke(sync, ['--config-dir', td, 'status'])
        # Should not crash; may report offline or defaults
        assert result.exit_code == 0
        assert 'State' in result.output


def test_config_show():
    runner = CliRunner()
    result = runner.invoke(sync, ['config'])
    assert result.exit_code == 0
    assert 'endpoint' in result.output.lower()


def test_queue_list():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as td:
        result = runner.invoke(sync, ['--config-dir', td, 'queue', 'list'])
        assert result.exit_code == 0
        assert 'Sync Queue' in result.output


def test_queue_subgroup_help():
    runner = CliRunner()
    result = runner.invoke(sync, ['queue', '--help'])
    assert result.exit_code == 0
    assert 'Manage the sync queue' in result.output


def test_export_help():
    runner = CliRunner()
    result = runner.invoke(sync, ['export', '--help'])
    assert result.exit_code == 0
    assert '--site' in result.output


def test_push_help():
    runner = CliRunner()
    result = runner.invoke(sync, ['push', '--help'])
    assert result.exit_code == 0
    assert 'Push pending bundles' in result.output


def test_queue_clean():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as td:
        result = runner.invoke(sync, ['--config-dir', td, 'queue', 'clean'])
        assert result.exit_code == 0
        assert 'Cleaned' in result.output
