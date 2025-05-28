# AdvancedTracking
MCDR plugin used to track customary items

**English**

## Features

1. Use carpetscript to track player actions with specific limits
   - Actions
     - [ ] Block placement
     - [ ] Block breaking
     - [ ] non-AFK time
   - Limits
     - [ ] Area (by player position)
     - [ ] block_type
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
        "group_name": {
            "area": {
                "x_min":-10, 
                "x_max":10, 
                "z_min":-10, 
                "z_max":10
            }, 
            "trackers": [
                {
                    "item": "item_name", 
                    "area": {
                        "x_min":-10, 
                        "x_max":10, 
                        "z_min":-10, 
                        "z_max":10
                    }, 
                    "specs":{
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
            ]
        }
    }
}
```
### player tracking data
#### **`example_uuid.json`**: 
```json
{
    "player_ID":"__VY__", 
    "items": {
        "item_name": 0
    }
}
```