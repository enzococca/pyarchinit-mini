"""
Script per configurare automaticamente Claude Desktop con PyArchInit-Mini MCP.

Questo script:
1. Cerca il file di configurazione di Claude Desktop
2. Controlla se uvx è installato
3. Aggiunge la configurazione MCP per PyArchInit-Mini
4. Gestisce sia file nuovi che esistenti con altre configurazioni
"""

import json
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


def get_claude_config_path() -> Optional[Path]:
    """
    Trova il path del file di configurazione di Claude Desktop.

    Returns:
        Path al file di config, o None se non trovato
    """
    if sys.platform == "darwin":  # macOS
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        appdata = os.getenv("APPDATA")
        if appdata:
            config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
        else:
            return None
    else:  # Linux
        config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

    return config_path if config_path.parent.exists() else None


def check_uvx_installed() -> bool:
    """
    Controlla se uvx è installato.

    Returns:
        True se uvx è installato, False altrimenti
    """
    return shutil.which("uvx") is not None


def check_claude_installed() -> bool:
    """
    Controlla se Claude Desktop è installato verificando la directory di configurazione.

    Returns:
        True se Claude è installato, False altrimenti
    """
    config_path = get_claude_config_path()
    return config_path is not None and config_path.parent.exists()


def load_claude_config(config_path: Path) -> Dict[str, Any]:
    """
    Carica la configurazione esistente di Claude Desktop.

    Args:
        config_path: Path al file di configurazione

    Returns:
        Dizionario con la configurazione esistente, o un dict vuoto se il file non esiste
    """
    if not config_path.exists():
        return {"mcpServers": {}}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Assicura che mcpServers esista
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            return config
    except json.JSONDecodeError:
        print(f"⚠️  File di configurazione corrotto: {config_path}")
        print("   Verrà creato un backup e una nuova configurazione")
        return {"mcpServers": {}}
    except Exception as e:
        print(f"⚠️  Errore durante la lettura della configurazione: {e}")
        return {"mcpServers": {}}


def add_pyarchinit_config(config: Dict[str, Any]) -> bool:
    """
    Aggiunge la configurazione MCP di PyArchInit-Mini.

    Args:
        config: Dizionario di configurazione di Claude Desktop

    Returns:
        True se la configurazione è stata aggiunta/aggiornata, False se già esistente
    """
    pyarchinit_config = {
        "command": "uvx",
        "args": ["--from", "pyarchinit-mini", "pyarchinit-mini-mcp"]
    }

    # Controlla se la configurazione esiste già
    if "pyarchinit" in config["mcpServers"]:
        existing = config["mcpServers"]["pyarchinit"]
        if existing == pyarchinit_config:
            return False  # Già configurato correttamente

    # Aggiungi o aggiorna la configurazione
    config["mcpServers"]["pyarchinit"] = pyarchinit_config
    return True


def save_claude_config(config_path: Path, config: Dict[str, Any], backup: bool = True):
    """
    Salva la configurazione di Claude Desktop.

    Args:
        config_path: Path al file di configurazione
        config: Dizionario di configurazione da salvare
        backup: Se True, crea un backup del file esistente
    """
    # Crea la directory se non esiste
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Crea backup se richiesto e il file esiste
    if backup and config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print(f"  ✓ Backup creato: {backup_path}")

    # Salva la nuova configurazione
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Aggiungi newline finale


def configure_claude_desktop(silent: bool = False, force: bool = False) -> int:
    """
    Configura Claude Desktop con PyArchInit-Mini MCP.

    Args:
        silent: Se True, non stampa output
        force: Se True, sovrascrive la configurazione esistente

    Returns:
        0 se successo, codice di errore altrimenti
    """
    if not silent:
        print("=" * 70)
        print("Configurazione Claude Desktop per PyArchInit-Mini MCP")
        print("=" * 70)

    # 1. Controlla se Claude è installato
    if not silent:
        print("\n1. Controllo installazione Claude Desktop...")

    if not check_claude_installed():
        print("  ⚠️  Claude Desktop non sembra essere installato")
        print("     Directory di configurazione non trovata")
        print("\n     Per installare Claude Desktop:")
        print("     https://claude.ai/download")
        return 1

    if not silent:
        print("  ✓ Claude Desktop installato")

    # 2. Controlla se uvx è installato
    if not silent:
        print("\n2. Controllo installazione uvx...")

    if not check_uvx_installed():
        print("  ⚠️  uvx non è installato")
        print("\n     Per installare uvx:")
        print("     pip install uv")
        print("     - oppure -")
        print("     curl -LsSf https://astral.sh/uv/install.sh | sh")
        return 2

    if not silent:
        print("  ✓ uvx installato")

    # 3. Trova e carica la configurazione
    if not silent:
        print("\n3. Configurazione file di config...")

    config_path = get_claude_config_path()
    if not config_path:
        print("  ✗ Impossibile determinare il path di configurazione")
        return 3

    if not silent:
        print(f"  • File di config: {config_path}")

    config = load_claude_config(config_path)

    # 4. Aggiungi la configurazione PyArchInit
    was_updated = add_pyarchinit_config(config)

    if not was_updated and not force:
        if not silent:
            print("  • PyArchInit MCP già configurato correttamente")
            print("\n✓ Configurazione già presente e aggiornata!")
        return 0

    # 5. Salva la configurazione
    try:
        save_claude_config(config_path, config, backup=True)
        if not silent:
            print("  ✓ Configurazione salvata")
    except Exception as e:
        print(f"  ✗ Errore durante il salvataggio: {e}")
        return 4

    # 6. Riepilogo
    if not silent:
        print("\n" + "=" * 70)
        print("✓ Configurazione completata con successo!")
        print("=" * 70)
        print("\nConfigurazione aggiunta:")
        print("  {")
        print('    "mcpServers": {')
        print('      "pyarchinit": {')
        print('        "command": "uvx",')
        print('        "args": ["--from", "pyarchinit-mini", "pyarchinit-mini-mcp"]')
        print('      }')
        print('    }')
        print("  }")

        print("\nProssimi passi:")
        print("  1. Riavvia Claude Desktop")
        print("  2. Apri una nuova conversazione")
        print("  3. PyArchInit-Mini MCP sarà disponibile automaticamente")

        print("\nComandi disponibili in Claude:")
        print("  • get_schema - Visualizza schema database")
        print("  • insert_data - Inserisci dati")
        print("  • update_data - Aggiorna dati")
        print("  • delete_data - Elimina dati")
        print("  • manage_service - Gestisci servizi (web, api, gui)")
        print("  • create_harris_matrix - Crea matrice Harris")
        print("  • validate_stratigraphy - Valida stratigrafia")
        print("  • ...e molti altri!")

        print("\n" + "=" * 70)

    return 0


def main():
    """Entry point per lo script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configura Claude Desktop con PyArchInit-Mini MCP"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Modalità silenziosa (nessun output)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forza la sovrascrittura della configurazione esistente"
    )

    args = parser.parse_args()

    return configure_claude_desktop(silent=args.silent, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
