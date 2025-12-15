# Team Profile Feature

## Overview

The team profile feature allows users to view detailed information about individual teams by clicking on their names from the scoreboard. This provides a public view of team details and their solved challenges.

## Features

### Team Information Display
- **Rank**: Current position on the scoreboard
- **Score**: Total points earned
- **Country**: Team's country (if provided)
- **Affiliation**: Organization or institution (if provided)
- **Website**: Team's website with external link (if provided)
- **Member Since**: Registration date

### Solved Challenges
- List of all challenges solved by the team
- Challenge name, category, and point value
- Date of solve
- Visual indicators for achievements

## Implementation Details

### Backend Components

#### 1. CTFd Client (`ctfd_client.py`)
Added two new methods:

```python
def get_team_details(self, team_id):
    """Fetch detailed information about a specific team"""
    # Calls CTFd API: GET /api/v1/teams/{team_id}
    
def get_team_solves(self, team_id):
    """Fetch the list of challenges solved by a specific team"""
    # Calls CTFd API: GET /api/v1/teams/{team_id}/solves
```

#### 2. Flask Route (`app.py`)
Added new route for team profiles:

```python
@app.route('/team/<int:team_id>')
def team_profile(team_id):
    """Team profile page showing team details and solves"""
    # Fetches team data from CTFd API
    # Enriches with rank/score from local database
    # Renders team_profile.html template
```

### Frontend Components

#### 1. Team Profile Template (`templates/team_profile.html`)
- Responsive design with gradient background
- Card-based layout for team information
- Grid layout for solved challenges
- Hover effects and transitions
- Back navigation to scoreboard

#### 2. Updated Scoreboard (`templates/index.html`)
- Team names are now clickable links
- Hover effect shows link cursor
- External link icon indicator
- Smooth transition on hover

## Usage

### For Users
1. Visit the scoreboard at `http://localhost:5000/`
2. Click on any team name in the scoreboard
3. View the team's profile with details and solves
4. Click "Back to Scoreboard" to return

### For Developers
Access team profiles programmatically:
```
GET /team/{team_id}
```

Example:
```
GET /team/123
```

## API Endpoints Used

### CTFd API
- `GET /api/v1/teams/{team_id}` - Get team details
- `GET /api/v1/teams/{team_id}/solves` - Get team's solved challenges

## Testing

Run the test script to verify the feature:
```bash
python test_team_profile.py
```

This will:
1. Initialize the CTFd client
2. Fetch the scoreboard
3. Fetch details for a team
4. Fetch solves for a team
5. Verify database integration

## Styling

The team profile page uses:
- **Color Scheme**: Purple and cyan gradients matching the main theme
- **Animations**: Smooth transitions on hover
- **Icons**: FontAwesome for visual elements
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Dark Theme**: Consistent with the scoreboard design

## Error Handling

- If team not found: Shows error page with message
- If API fails: Displays error message
- If no solves: Shows "No challenges solved yet" message
- Gracefully handles missing optional fields (country, website, etc.)

## Security Considerations

- Read-only public view
- No authentication required (public scoreboard feature)
- Only displays information already public in CTFd
- No modification capabilities
- CSRF protection through Flask's security headers

## Future Enhancements

Possible improvements:
1. Team member list display
2. Solve timeline/graph
3. Category statistics
4. Compare with other teams
5. Export team statistics
6. Share team profile link
7. Award/badge display

## Screenshots

### Team Profile Page Layout
```
┌─────────────────────────────────────────┐
│  ← Back to Scoreboard                    │
│                                          │
│  Team Name                               │
│  Team Profile                            │
│                                          │
│  ┌────────────┬────────────┐            │
│  │ Rank: #1   │ Country    │            │
│  │ Score: 1000│ Affiliation│            │
│  └────────────┴────────────┘            │
│                                          │
│  Solved Challenges (15)                  │
│  ┌──────┬──────┐                        │
│  │ Chal │ Chal │                        │
│  │  1   │  2   │                        │
│  └──────┴──────┘                        │
│  ┌──────┬──────┐                        │
│  │ Chal │ Chal │                        │
│  │  3   │  4   │                        │
│  └──────┴──────┘                        │
│                                          │
│  [Back to Scoreboard]                    │
└─────────────────────────────────────────┘
```

## Dependencies

No new dependencies required. Uses existing:
- Flask
- requests
- Jinja2 templates
- FontAwesome (CDN)
- DaisyUI/Tailwind CSS (CDN)

## Configuration

No additional configuration needed. Uses existing environment variables from `.env`:
- `CTFD_API_URL`
- `CTFD_API_KEY`
- `CTFD_EVENT_NAME`

