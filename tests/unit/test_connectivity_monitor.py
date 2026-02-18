"""Test connectivity monitor."""
from pyarchinit_mini.stratigraph.connectivity_monitor import ConnectivityMonitor


def test_initial_state_is_offline():
    monitor = ConnectivityMonitor(health_url="http://localhost:99999/health")
    assert monitor.is_online is False


def test_debounce_logic():
    monitor = ConnectivityMonitor(
        health_url="http://localhost:99999/health",
        debounce_count=2
    )
    changes = []
    monitor.on_connectivity_changed(lambda online: changes.append(online))

    # Simulate probe results: 2 consecutive True should flip state
    monitor._update_state(True)
    assert len(changes) == 0  # debounce not yet met
    monitor._update_state(True)
    assert len(changes) == 1
    assert changes[0] is True
    assert monitor.is_online is True


def test_stop_cancels_timer():
    monitor = ConnectivityMonitor(health_url="http://localhost:99999/health")
    monitor.start()
    monitor.stop()
    assert monitor._running is False
