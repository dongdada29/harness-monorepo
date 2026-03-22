#!/bin/bash
# state.sh - State management utility
# Usage: ./scripts/state.sh <action> [args]

set -e

STATE_FILE="harness/feedback/state/state.json"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

# Ensure directory exists
mkdir -p "$(dirname "$STATE_FILE")"

# Ensure state file exists
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << 'EOF'
{
  "project": "",
  "version": "1.0.0",
  "lastUpdated": "",
  "currentTask": null,
  "taskStatus": "idle",
  "taskStartedAt": null,
  "taskCompletedAt": null,
  "checkpoints": {
    "CP1": "pending",
    "CP2": "pending",
    "CP3": "pending",
    "CP4": "pending",
    "CP5": "pending"
  },
  "gates": {
    "lint": "pending",
    "typecheck": "pending",
    "test": "pending",
    "build": "pending"
  },
  "blockedBy": null,
  "todo": [],
  "recentChanges": [],
  "stats": {
    "tasksCompleted": 0,
    "tasksBlocked": 0,
    "averageTaskDuration": null
  }
}
EOF
fi

case "$1" in
    "start")
        TASK="$2"
        if [ -z "$TASK" ]; then
            echo "Usage: state.sh start <task_name>"
            exit 1
        fi
        # Update state for new task
        python3 << EOF
import json

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

state['currentTask'] = '$TASK'
state['taskStatus'] = 'in_progress'
state['taskStartedAt'] = '$DATE $TIME'
state['checkpoints'] = {
    'CP1': 'in_progress',
    'CP2': 'pending',
    'CP3': 'pending',
    'CP4': 'pending',
    'CP5': 'pending'
}
state['gates'] = {
    'lint': 'pending',
    'typecheck': 'pending',
    'test': 'pending',
    'build': 'pending'
}
state['blockedBy'] = None
state['lastUpdated'] = '$DATE $TIME'

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f"✅ Task started: $TASK")
EOF
        ;;
    
    "done")
        python3 << EOF
import json
from datetime import datetime

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

task = state['currentTask']
started = state['taskStartedAt']

# Calculate duration
if started:
    start_time = datetime.strptime(started, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime('$DATE $TIME', '%Y-%m-%d %H:%M:%S')
    duration_min = int((end_time - start_time).total_seconds() / 60)
else:
    duration_min = 0

state['currentTask'] = None
state['taskStatus'] = 'completed'
state['taskCompletedAt'] = '$DATE $TIME'
state['checkpoints']['CP5'] = 'passed'
state['lastUpdated'] = '$DATE $TIME'

# Add to recent changes
state['recentChanges'].insert(0, {
    'date': '$DATE',
    'task': task,
    'status': 'completed',
    'duration': duration_min,
    'by': 'agent'
})

# Update stats
state['stats']['tasksCompleted'] += 1

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f"✅ Task completed: {task}")
print(f"⏱️  Duration: {duration_min} minutes")
EOF
        ;;
    
    "blocked")
        REASON="$2"
        if [ -z "$REASON" ]; then
            echo "Usage: state.sh blocked <reason>"
            exit 1
        fi
        python3 << EOF
import json

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

state['taskStatus'] = 'blocked'
state['blockedBy'] = '$REASON'
state['lastUpdated'] = '$DATE $TIME'
state['stats']['tasksBlocked'] += 1

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f"🚧 Task blocked: $REASON")
EOF
        ;;
    
    "update-gate")
        GATE="$2"
        STATUS="$3"
        python3 << EOF
import json

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

state['gates']['$GATE'] = '$STATUS'
state['lastUpdated'] = '$DATE $TIME'

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f"Gate $GATE: $STATUS")
EOF
        ;;
    
    "update-cp")
        CP="$2"
        STATUS="$3"
        python3 << EOF
import json

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

state['checkpoints']['$CP'] = '$STATUS'
state['lastUpdated'] = '$DATE $TIME'

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f"Checkpoint $CP: $STATUS")
EOF
        ;;
    
    "show")
        cat "$STATE_FILE" | python3 -m json.tool
        ;;
    
    *)
        echo "Usage: state.sh <action> [args]"
        echo ""
        echo "Actions:"
        echo "  start <task>      - Start a new task"
        echo "  done              - Mark current task as done"
        echo "  blocked <reason>  - Mark task as blocked"
        echo "  update-gate <gate> <status>  - Update gate status"
        echo "  update-cp <cp> <status>      - Update checkpoint status"
        echo "  show              - Show current state"
        ;;
esac
