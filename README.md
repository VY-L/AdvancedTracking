# AdvancedTracking
MCDR plugin used to track customary player events

**English**

## Features

1. Use carpetscript to track player actions with specific limits
   - Actions
     - [x] Block placement
     - [x] Block breaking
     - [ ] non-AFK time
   - Limits
     - [x] Area (by player position)
     - [x] block_type
     - [ ] playerID
2. Create scoreboards based on the trackers
   - [ ] Weighted sum
3. Use MCDR as user interface to manage tracking system


## Other TODOs
- Lang
- Usages, How It works in README.md
- Variable update mechanisms

## Data schemes
### tracker structure
#### **`trackers.json`**: 
```json
{
    "player_break_blocks": {
        "group_id": { 
            "area": {
                "x_min":-10, 
                "x_max":10, 
                "z_min":-10, 
                "z_max":10
            }, 
            "trackers": {
                "tracker_id": { 
                    "area": {
                        "x_min":-10, 
                        "x_max":10, 
                        "z_min":-10, 
                        "z_max":10
                    }, 
                    "components":{
                        "component_id": {
                            "area": {
                                "x_min":-10, 
                                "x_max":10, 
                                "z_min":-10, 
                                "z_max":10
                            }, 
                            "block_type":{
                                "whitelist": {}, 
                                "blacklist": {
                                    "smooth_stone_slab": [
                                        {"type":"bottom"}, 
                                        {"type":"top", "waterlogged":true}
                                    ]
                                }, 
                                "mode": "blacklist"
                            }
                        }
                    }
                }
            }
        }
    }
}
```
### player tracking data
#### **`example_uuid.json`**: 
```json
{
    "player_ID":"__VY__", 
    "trackers": {
        "tracker_id": 0
    }
}
```
### scoreboard configuration
#### **`scoreboards.json`**: 
```json
{
    "scoreboard_id": {
        "display_name": "Scoreboard Display", 
        "mode": "weighted_sum", 
        "trackers": [
            {
                "tracjer_id": "tracker_id", 
                "weight":1
            }
        ]
    }
}
```