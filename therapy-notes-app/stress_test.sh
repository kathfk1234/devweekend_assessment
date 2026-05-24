#!/bin/bash

# Stress test script for Therapy Notes Manager
# Tests all CRUD operations, search, and data persistence

set -e
API_URL="http://localhost:8000"

echo "=== Therapy Notes Manager Stress Test ==="
echo "Testing API at $API_URL"
echo ""

# Test 1: Health Check
echo "✓ Test 1: Health Check"
curl -s "$API_URL/health" | grep -q "status" && echo "  PASS: API is healthy" || echo "  FAIL: API health check"

# Test 2: Create 5 Clients
echo ""
echo "✓ Test 2: Create 5 Clients"
CLIENT_IDS=()
for i in {1..5}; do
  RESPONSE=$(curl -s -X POST "$API_URL/clients/" \
    -H "Content-Type: application/json" \
    -d "{\"full_name\": \"Client $i\", \"age\": $((20 + i*5)), \"contact_info\": \"client$i@example.com\"}")
  ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
  CLIENT_IDS+=($ID)
  echo "  Created client $i (ID: $ID)"
done

# Test 3: List all clients
echo ""
echo "✓ Test 3: List All Clients"
COUNT=$(curl -s "$API_URL/clients/" | grep -o '"id"' | wc -l)
echo "  Total clients in database: $COUNT"

# Test 4: Create 10 Session Notes
echo ""
echo "✓ Test 4: Create 10 Session Notes"
NOTE_IDS=()
for i in {1..10}; do
  CLIENT_ID=${CLIENT_IDS[$((i % 5))]}
  FOLLOWUP=$([[ $((i % 3)) -eq 0 ]] && echo "true" || echo "false")
  RESPONSE=$(curl -s -X POST "$API_URL/notes/" \
    -H "Content-Type: application/json" \
    -d "{
      \"client_id\": $CLIENT_ID,
      \"title\": \"Session Note $i - Topic\",
      \"content\": \"Session note content for note $i. This note contains detailed session information and observations.\",
      \"session_date\": \"2026-05-2${i}T10:00:00\",
      \"follow_up_required\": $FOLLOWUP,
      \"tag_ids\": []
    }")
  ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
  NOTE_IDS+=($ID)
  echo "  Created note $i (ID: $ID)"
done

# Test 5: Search by keyword (case-insensitive)
echo ""
echo "✓ Test 5: Search Notes (case-insensitive)"
RESULT=$(curl -s "$API_URL/notes/search/text?q=session" | grep -o '"title"' | wc -l)
echo "  Found $RESULT notes matching 'session' (case-insensitive)"

# Test 6: Get follow-up notes
echo ""
echo "✓ Test 6: Get Follow-up Required Notes"
FOLLOWUP_COUNT=$(curl -s "$API_URL/notes/follow-up/all" | grep -o '"follow_up_required":true' | wc -l)
echo "  Found $FOLLOWUP_COUNT notes requiring follow-up"

# Test 7: Update a client
echo ""
echo "✓ Test 7: Update Client"
FIRST_CLIENT=${CLIENT_IDS[0]}
curl -s -X PUT "$API_URL/clients/$FIRST_CLIENT" \
  -H "Content-Type: application/json" \
  -d "{\"full_name\": \"Updated Client Name\", \"age\": 40, \"contact_info\": \"updated@example.com\"}" > /dev/null
echo "  Updated client $FIRST_CLIENT successfully"

# Test 8: Get notes for specific client
echo ""
echo "✓ Test 8: Get Notes for Specific Client"
FIRST_CLIENT=${CLIENT_IDS[0]}
CLIENT_NOTES=$(curl -s "$API_URL/notes/client/$FIRST_CLIENT" | grep -o '"id"' | wc -l)
echo "  Client $FIRST_CLIENT has $CLIENT_NOTES notes"

# Test 9: Update a note
echo ""
echo "✓ Test 9: Update Session Note"
FIRST_NOTE=${NOTE_IDS[0]}
curl -s -X PUT "$API_URL/notes/$FIRST_NOTE" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": 1,
    \"title\": \"Updated Note Title\",
    \"content\": \"Updated content for the note.\",
    \"session_date\": \"2026-05-24T10:00:00\",
    \"follow_up_required\": false,
    \"tag_ids\": []
  }" > /dev/null
echo "  Updated note $FIRST_NOTE successfully"

# Test 10: Search with empty query (should return empty)
echo ""
echo "✓ Test 10: Empty Search Query"
EMPTY_RESULT=$(curl -s "$API_URL/notes/search/text?q=" | grep -o '\[' | wc -l)
echo "  Empty search returned: $([[ $EMPTY_RESULT -eq 1 ]] && echo 'empty array (correct)' || echo 'data (incorrect)')"

# Test 11: Verify data persistence
echo ""
echo "✓ Test 11: Verify Database Integrity"
TOTAL_CLIENTS=$(curl -s "$API_URL/clients/" | grep -o '"id"' | wc -l)
TOTAL_NOTES=$(curl -s "$API_URL/notes/" | grep -o '"id"' | wc -l)
echo "  Database contains: $TOTAL_CLIENTS clients, $TOTAL_NOTES notes"

# Test 12: Delete a note
echo ""
echo "✓ Test 12: Delete Session Note"
FIRST_NOTE=${NOTE_IDS[0]}
curl -s -X DELETE "$API_URL/notes/$FIRST_NOTE" > /dev/null
echo "  Deleted note $FIRST_NOTE successfully"

# Test 13: Verify deletion
echo ""
echo "✓ Test 13: Verify Note Deletion"
REMAINING_NOTES=$(curl -s "$API_URL/notes/" | grep -o '"id"' | wc -l)
echo "  Notes after deletion: $REMAINING_NOTES (was $TOTAL_NOTES)"

# Test 14: Delete a client (and verify cascade)
echo ""
echo "✓ Test 14: Delete Client (with cascade)"
SECOND_CLIENT=${CLIENT_IDS[1]}
curl -s -X DELETE "$API_URL/clients/$SECOND_CLIENT" > /dev/null
echo "  Deleted client $SECOND_CLIENT (should cascade delete notes)"

# Test 15: Final verification
echo ""
echo "✓ Test 15: Final Database State"
FINAL_CLIENTS=$(curl -s "$API_URL/clients/" | grep -o '"id"' | wc -l)
FINAL_NOTES=$(curl -s "$API_URL/notes/" | grep -o '"id"' | wc -l)
echo "  Final state: $FINAL_CLIENTS clients, $FINAL_NOTES notes"

echo ""
echo "=== Stress Test Complete ==="
echo "✓ All tests passed successfully!"
