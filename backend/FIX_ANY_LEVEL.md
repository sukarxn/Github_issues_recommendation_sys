# Fix: Handle "any" Experience Level Properly

## Problem
When `experience_level = "any"`, the system was returning **NO issues** instead of ALL issues.

### Root Cause
```python
# OLD CODE
wanted = set(EXPERIENCE_LEVEL_LABELS.get("any", []))
# → Returns empty set [] because "any" is not a key in EXPERIENCE_LEVEL_LABELS
# → Empty set intersection: labels & wanted = always False
# → Result: NO issues returned!
```

## Solution
Added special handling for the "any" case:

```python
# NEW CODE
if experience_level == "any":
    wanted = None  # No filtering - accept all issues
else:
    wanted = set(EXPERIENCE_LEVEL_LABELS.get(experience_level, []))

for item in r.json():
    if "pull_request" in item:
        continue
    
    if wanted is None:
        # Accept all issues without label filtering
        issues.append({...})
    else:
        # Filter by label for specific experience levels
        labels = {str(l.get("name", "")).strip().casefold() 
                 for l in item.get("labels", [])}
        if labels & wanted:
            issues.append({...})
```

## Impact

| Scenario | Before | After |
|----------|--------|-------|
| `experience_level = "beginner"` | ✅ Filters by beginner labels | ✅ Works (unchanged) |
| `experience_level = "intermediate"` | ✅ Filters by intermediate labels | ✅ Works (unchanged) |
| `experience_level = "advanced"` | ✅ Filters by advanced labels | ✅ Works (unchanged) |
| `experience_level = "any"` | ❌ Returns NO issues | ✅ Returns ALL issues |

## Code Changes

**File**: `/backend/core.py`
**Function**: `fetch_repo_good_first_issues()`
**Lines**: 263-321

### Key Changes:
1. Added condition: `if experience_level == "any"`
2. Set `wanted = None` for "any" level
3. Added nested if/else to handle both cases
4. When `wanted is None`, accept all issues
5. When `wanted` has labels, filter by intersection

## Testing

To test the fix:

```bash
# Test with "any" experience level
curl -X POST http://127.0.0.1:8001/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "student_profile": "Test profile",
    "language": "python",
    "per_page": 5
  }'
# Should now return issues without label filtering
```

## Benefits

✅ Users without a profile now get broader issue recommendations  
✅ System gracefully handles error cases that default to "any"  
✅ Backward compatible - doesn't affect beginner/intermediate/advanced  
✅ More intuitive behavior: "any" = no filtering

---

**Status**: ✅ IMPLEMENTED AND TESTED
