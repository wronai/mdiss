#!/bin/bash

# Test the ticket enhancement with the given command failure
TITLE="Fix: Test command 'make test-verbose' is failing"
COMMAND="make test-verbose"
ERROR_OUTPUT="""
make: *** No rule to make target 'test-verbose'.  Stop.
"""

# Create a temporary file for error output
ERROR_FILE=$(mktemp)
echo "$ERROR_OUTPUT" > "$ERROR_FILE"

# Run the enhancement script
python3 scripts/enhance_ticket.py \
    "$TITLE" \
    "$COMMAND" \
    "$ERROR_FILE" \
    > enhanced_ticket.json

# Display the enhanced ticket
echo "Enhanced ticket created: enhanced_ticket.json"
cat enhanced_ticket.json

# Clean up
rm "$ERROR_FILE"
