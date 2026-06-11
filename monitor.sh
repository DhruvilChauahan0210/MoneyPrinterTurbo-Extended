#!/bin/bash

TASK_ID="a91091a0-e3aa-4b60-9761-c1d95a6dce3a"
API="http://localhost:8080/api/v1/tasks/$TASK_ID"

echo "🎬 Monitoring World Cup video generation..."
echo "Task ID: $TASK_ID"
echo "-------------------------------------------"

while true; do
  RESPONSE=$(curl -s "$API" 2>/dev/null)
  STATE=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('state','?'))" 2>/dev/null)
  PROGRESS=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('progress','0'))" 2>/dev/null)

  TIMESTAMP=$(date '+%H:%M:%S')

  if [ "$STATE" = "1" ]; then
    echo "[$TIMESTAMP] ✅ DONE! Progress: 100%"
    osascript -e 'display notification "Your World Cup video is ready! 🎬⚽" with title "MoneyPrinter Done" sound name "Glass"'
    echo ""
    echo "Video saved at:"
    echo "storage/tasks/$TASK_ID/"
    break

  elif [ "$STATE" = "3" ]; then
    echo "[$TIMESTAMP] ❌ FAILED"
    osascript -e 'display notification "Video generation failed. Check logs." with title "MoneyPrinter Error" sound name "Basso"'
    break

  elif [ "$STATE" = "4" ]; then
    echo "[$TIMESTAMP] ⏳ Processing... $PROGRESS%"

  else
    echo "[$TIMESTAMP] State: $STATE | Progress: $PROGRESS%"
  fi

  sleep 30
done
