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
   - [ ] Weighted sums
3. Use MCDR as user interface to manage tracking system


## Usage

### Understanding structure

This plugin manages two things: Scoreboards and trackers

Scoreboards are always hooked up to in-game scoreboard objectives, currently with only one mode: the weighted sum of multiple trackers. Every scoreboard has the following attributes: objective, Display_name and key-value pairs of trackers and their weight

Trackers tracker specific actions. They are organized into groups but only for optimization (that I dont even know if it worths it). Every tracker falls into a tracker category, currently only implemented player_break_blocks, and player_place_blocks. They would have a tracker_id; an area, in which behavior may be counted (again for optimization), and components. Each component, again will have an area, in which behavior is considered, and a block_type filter, which is a whitelist or blacklist of blocks that would count. You can also whitelist/blacklist specific blockstates, see the example data schemes for more.

For example, if I have a project with a machine built in a perimeter, I may have a tracker called "trenchDigging", having 4 components, for each trench since each component's area can only be a cuboid. Then I may have another "obyDigging" tracker with only 1 component, recording the amount of obsidian each player dug within the perimeter. Then, there may be a "MachineBuilding" tracker for the placement of blocks within the machine, and a "DecoBuilding" Tracker to track the contribution towards building the decoration.

Then, you may create dedicated scoreboards for each tracker, and also probably a total scoreboard, as the general "contribution" to the whole project

For many of these repeating patters, there would be presets such as for trenches. Using such a preset, say "trench_preset", the plugin can automaticly create a tracker with 4 components, recording the blocks dug within the trench. This is also (when I finish) the recommended way of creating trackers.

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