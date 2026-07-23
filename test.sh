UNITX_HOME=/home/unitx
LOG_DIR=$UNITX_HOME/unitx_data/logs
LOG_FILE=$LOG_DIR/prod.log
mkdir -p "$LOG_DIR"
if [ ! -f $LOG_FILE ]; then
  touch $LOG_FILE
  chmod 777 $LOG_FILE
fi

# Prevent duplicate clicks
LOCK_FILE="${UNITX_HOME}/prod_run.lock"
export LOCK_FILE
if [ -f "$LOCK_FILE" ]; then
  echo "ProdX run.sh is already running (locuk file exists)." >> $LOG_DIR/prod.log
  exit 1
fi

# Check if backtest_prod container is running (mutual exclusion)
if docker ps --format "table {{.Names}}" | grep -q "backtest_prod"; then
  echo "Error: backtest_prod container is already running. Cannot start ProdX container." >> $LOG_DIR/prod.log

echo "Camera was not Founded"

echo "Please check the configration file"
