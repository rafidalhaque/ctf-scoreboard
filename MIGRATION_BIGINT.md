# Migration Guide: team_id INTEGER to BIGINT

## Issue
The `team_id` column was defined as `INTEGER` which has a maximum value of 2,147,483,647. 

The application generates `team_id` values in two ways:
1. **From CTFd API**: Uses the `account_id` field directly from the API response (database.py line 34)
2. **From string entries**: Generates a hash using SHA256 and takes first 8 hex characters (database.py line 42)

This caused errors when:
- Hash values generated from team names exceeded the INTEGER limit (e.g., 3564330554)
- CTFd `account_id` values from the API exceeded the INTEGER limit

Error message:
```
value "3564330554" is out of range for type integer
```

## Solution
Changed `team_id` from `INTEGER` to `BIGINT` which supports values up to 9,223,372,036,854,775,807.

## Migration Steps for Existing Deployments

If you already have a database with the old schema, follow these steps to migrate:

### Option 1: For databases with no critical data (Recommended for development)
Simply drop and recreate the table:

```sql
-- Drop existing table
DROP TABLE IF EXISTS scoreboard CASCADE;

-- Run the new schema.sql file
-- (Copy and paste the entire contents of schema.sql)
```

### Option 2: For production databases with existing data
Alter the existing column to BIGINT:

```sql
-- Alter the team_id column type
ALTER TABLE scoreboard 
ALTER COLUMN team_id TYPE BIGINT;

-- Verify the change
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'scoreboard' AND column_name = 'team_id';
```

### Verification
After migration, verify the column type is correct:

```sql
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'scoreboard'
ORDER BY ordinal_position;
```

Expected output should show `team_id` as `bigint`.

### Data Refresh (IMPORTANT!)
After migrating the schema, you need to refresh the scoreboard data because:
- Failed upserts during the integer overflow period may have left stale or corrupted data
- The database needs fresh data from CTFd API with the correct column type

**Option A: Using the provided script (Recommended)**
```bash
python fix_data.py
```

**Option B: Manual SQL**
```sql
-- Clear existing data
DELETE FROM scoreboard;

-- Restart your application to fetch fresh data
-- The scheduler will automatically populate the table
```

After refreshing the data, verify that:
1. Team names display as strings (not numbers)
2. Scores show actual values (not all zeros)

### Testing
After migration and data refresh, monitor the logs. The error should no longer occur:

```bash
# Monitor application logs
tail -f /path/to/your/logs

# Or if using Docker:
docker logs -f <container_name>
```

## Troubleshooting

### Issue: Team names show as numbers instead of strings
**Symptom**: The scoreboard displays numerical values in the team name column.

**Cause**: This indicates data corruption or stale data from the period when upserts were failing.

**Solution**: Clear the database and let the system fetch fresh data:
```bash
python fix_data.py
```

### Issue: All scores show 0
**Symptom**: All teams have a score of 0 even though they should have points.

**Cause**: Similar to above - stale or corrupted data from failed upserts.

**Solution**: Clear the database and refresh data as described above.

### Issue: Error persists after migration
**Symptom**: The integer overflow error still occurs after running the ALTER TABLE command.

**Possible causes**:
1. The ALTER TABLE didn't complete successfully - verify with `\d scoreboard` in psql
2. You're running an old version of the application - ensure you've pulled latest code
3. Connection pooling issues - restart your application completely

## Notes
- The migration from INTEGER to BIGINT is safe and does not lose data
- All existing values in the INTEGER range are valid BIGINT values
- No application code changes are required - Python handles both integer sizes transparently
- Indexes on `team_id` will be automatically updated during the ALTER TABLE operation
- **Important**: After migration, you MUST refresh the data using `fix_data.py` to ensure clean data
