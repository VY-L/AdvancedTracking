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


## Usage

### Commands

Base command : `!!at`

`!!at clicker` to enter click-to-use version gui

`!!at tracker add <tracker_name> <tracker_type>`

`!!at tracker add <tracker_name> preset <preset_name> ...`

`!!at component add <tracker_name> <component_name>`

`!!at component area <tracker_name> <component_name> single <attr> <value>`

`!!at component area <tracker_name> <component_name> cuboid <x1> <y1> <z1> <x2> <y2> <z2>`

`!!at component area <tracker_name> <component_name> rectangle <x1> <z1> <x2> <z2>`

`!!at component block_type <tracker_name> <component_name> blacklist set <blacklist>`

`!!at component block_type <tracker_name> <component_name> whitelist set <ehitelist>`

`!!at component block_type <tracker_name> <component_name> blacklist add <instance>`

`!!at component block_type <tracker_name> <component_name> whitelist add <instance>`

`!!at tracker delete <tracker_name>` Note: this will clear all data too


`!!at scoreboard create <scoreboard_name>`

`!!at scoreboard create <scoreboard_name> <"Display Name">`

`!!at scoreboard create <scoreboard_name> <"Display Name"> <tracker_name>`

`!!at scoreboard preset <preset_name> <scoreboard_name> ...`

`!!at scoreboard add <scoreboard_name> <tracker_name> weight`


## Other TODOs
- Lang
- Usages, How It works in README.md
- Variable update mechanisms
- add type for Area, BlockType

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