#!/bin/bash
cd ~/projects/ToxScreen-AI
source venv/bin/activate
python3 -c "from modules.government_db import auto_sync_daily; count = auto_sync_daily(); print(f'Synced {count} compounds')"
