#!/bin/bash
"""
AI Link Scraper Daily Service Startup Script

This script can be used to:
1. Start the daily scheduler as a system service
2. Install as a cron job
3. Run manually for testing
"""

# Set up environment
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Function to install schedule package if needed
install_dependencies() {
    echo "🔧 Installing required dependencies..."
    pip install schedule
}

# Function to run daily scheduler
run_scheduler() {
    echo "🤖 Starting AI Link Scraper Daily Scheduler..."
    cd "$SCRIPT_DIR"
    python daily_scheduler.py
}

# Function to run manual update
run_manual_update() {
    echo "🔧 Running manual daily update..."
    cd "$SCRIPT_DIR"
    python daily_scheduler.py --run-now
}

# Function to show status
show_status() {
    echo "📊 Checking scheduler status..."
    cd "$SCRIPT_DIR"
    python daily_scheduler.py --status
}

# Function to install as cron job
install_cron() {
    echo "⏰ Installing daily cron job..."
    
    # Create cron job that runs at 9:00 AM daily
    CRON_COMMAND="0 9 * * * cd $SCRIPT_DIR && python daily_scheduler.py --run-now >> logs/cron.log 2>&1"
    
    # Add to crontab if not already exists
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
    
    echo "✅ Cron job installed! The scraper will run daily at 9:00 AM"
    echo "📄 Logs will be saved to: $SCRIPT_DIR/logs/cron.log"
    echo "🔍 To view cron jobs: crontab -l"
    echo "🗑️  To remove cron job: crontab -e"
}

# Function to create systemd service
create_systemd_service() {
    echo "🔧 Creating systemd service..."
    
    SERVICE_NAME="ai-link-scraper"
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=AI Link Scraper Daily Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment=PYTHONPATH=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/start_daily_service.sh run-scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    echo "✅ Systemd service created: $SERVICE_NAME"
    echo "🚀 To start: sudo systemctl start $SERVICE_NAME"
    echo "📊 To check status: sudo systemctl status $SERVICE_NAME"
    echo "📄 To view logs: sudo journalctl -u $SERVICE_NAME -f"
}

# Main script logic
case "${1:-help}" in
    "run-scheduler")
        install_dependencies
        run_scheduler
        ;;
    "run-now")
        install_dependencies
        run_manual_update
        ;;
    "status")
        show_status
        ;;
    "install-cron")
        install_cron
        ;;
    "install-systemd")
        create_systemd_service
        ;;
    "help"|*)
        echo "AI Link Scraper Daily Service"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  run-scheduler    Start the daily scheduler daemon"
        echo "  run-now         Run the daily update immediately"
        echo "  status          Show current status"
        echo "  install-cron    Install as daily cron job (9:00 AM)"
        echo "  install-systemd Create systemd service (requires sudo)"
        echo "  help            Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 run-now                 # Run update immediately"
        echo "  $0 install-cron            # Set up daily cron job"
        echo "  $0 run-scheduler           # Start persistent scheduler"
        echo ""
        ;;
esac
