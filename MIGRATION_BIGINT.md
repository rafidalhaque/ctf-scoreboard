# Migration Guide: team_id INTEGER to BIGINT

## Issue
The `team_id` column was defined as `INTEGER` which has a maximum value of 2,147,483,647. This caused errors when:
- Hash values generated from team names exceeded this limit
- CTFd `account_id` values exceeded this limit

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

### Testing
After migration, restart your application and monitor the logs. The error should no longer occur:

```bash
# Monitor application logs
tail -f /path/to/your/logs

# Or if using Docker:
docker logs -f <container_name>
```

## Notes
- The migration from INTEGER to BIGINT is safe and does not lose data
- All existing values in the INTEGER range are valid BIGINT values
- No application code changes are required - Python handles both integer sizes transparently
- Indexes on `team_id` will be automatically updated during the ALTER TABLE operation
