# AdvancedTracking
MCDR plugin used to track customary player events

**English** | [中文](README.zh_cn.md)

## Features

1. Use carpetscript to track player actions with specific limits
   - Actions
     - [x] Block placement
     - [x] Block breaking
     - [ ] non-AFK time
   - Limits
     - [x] Area (by player position)
     - [x] block_type
     - [ ] playerID/player state
2. Create scoreboards based on the trackers
   - [x] Weighted sums
3. Use MCDR as user interface to manage tracking system


## Usage

### Understanding structure

This plugin manages two things: Scoreboards and trackers

Scoreboards are always hooked up to in-game scoreboard objectives, currently with only one mode: the weighted sum of multiple trackers. Every scoreboard has the following attributes: objective, Display_name and key-value pairs of trackers and their weight

Trackers track specific actions. They are organized into groups but only for optimization (that I dont even know if it worths it). Every tracker falls into a tracker category, currently only implemented player_break_blocks, and player_place_blocks. They would have a tracker_id; an area, in which behavior may be counted (again for optimization), and components. Each component, again will have an area, in which behavior is considered, and a block_type filter, which is a whitelist or blacklist of blocks that would count. You can also whitelist/blacklist specific blockstates, see the example data schemes for more.

For example, if I have a project with a machine built in a perimeter, I may have a tracker called "trenchDigging", having 4 components, for each trench since each component's area can only be a cuboid. Then I may have another "obyDigging" tracker with only 1 component, recording the amount of obsidian each player dug within the perimeter. Then, there may be a "MachineBuilding" tracker for the placement of blocks within the machine, and a "DecoBuilding" Tracker to track the contribution towards building the decoration.

Then, you may create dedicated scoreboards for each tracker, and also probably a total scoreboard, as the general "contribution" to the whole project

For many of these repeating patters, there would be presets such as for trenches. Using such a preset, say "trench_preset", the plugin can automaticly create a tracker with 4 components, recording the blocks dug within the trench. This is also (when I finish) the recommended way of creating trackers.


### Commands

基础: `!!at`

`!!at` enter click menu (IDK when im gonna implement this)

`!!at help` see help

[//]: # (`!!at list presets` see all presets)

`!!at list tracker(s)` see all trackers

`!!at list tracker <scoreboard_name>` see all trackers in a scoreboard

`!!at list component <tracker_name>` see all components in a tracker

`!!at list scoreboard(s)` see all scoreboards

`!!at list scoreboard(s) <scoreboard_name>` see all trackers in a scoreboard


`!!at show tracker <tracker_name>` show detail of a tracker

`!!at show component <tracker_name> <component_name>` show detail of a component

`!!at show scoreboard <scoreboard_name>` show detail of a scoreboard


`!!at add tracker <tracker_name> <tracker_type>` create new empty tracker

`!!at add tracker <tracker_name> <preset_name> ...` create tracker by preset

[//]: # (<!-- `!!at add tracker <tracker_name> preset <preset_name> ...` create tracker by preset &#40;used to support future custom presets&#41; -->)

`!!at tracker <tracker_name> add <component_name>` create an empty component under a tracker

`!!at component <tracker_name> <component_name> create` same as above

`!!ad add component <tracker_name> <component_name>` same as above

`!!at tracker <tracker_name> delete/remove` delete a tracker, will delete all data in it too, needs `!!at confirm`

`!!at component <tracker_name> <component_name> attr <value>` change an area attribute of a component (Ex. change x_min to -1000)

`!!at component <tracker_name> <component_name> cuboid <x1> <y1> <z1> <x2> <y2> <z2>` overwrite/set area of certain component by 2 opposite vertices of a cuboid

`!!at component <tracker_name> <component_name> rectangle <x1> <z1> <x2> <z2>` Same as above, but rectange (ignore y-value)

`!!at component <tracker_name> <component_name> blacklist set <blacklist>` overwrite blacklist

`!!at component <tracker_name> <component_name> whitelist set <whitelist>`...

`!!at component <tracker_name> <component_name> blacklist add <instance>` add a block(state) to blacklist

`!!at component <tracker_name> <component_name> whitelist add <instance>`...

`!!at component <tracker_name> <component_name> blacklist` set to blacklist mode

`!!at component <tracker_name> <component_name> whitelist`

`!!at component <tracker_name> <component_name> remove/delete`

`!!at tracker <tracker_name> remove/delete <component_name>`


`!!at add scoreboard <scoreboard_name>`

`!!at add scoreboard <scoreboard_name> <"Display Name">`

`!!at add scoreboard <scoreboard_name> <"Display Name"> <tracker_name>` create a dedicated scoreboard for a tracker

`!!at scoreboard <scoreboard_name> preset <preset_name>` overwrite/create scoreboard by preset

`!!at scoreboard add <scoreboard_name> <tracker_name> <weight>` add a tracker-weight pair under a scoreboard

## Other TODOs
- Lang
- Usages, How It works in README.md
- Variable update mechanisms
- add type for Area, BlockType
- config command prefix
- attention is all you need (partial things)
- search for objects
- scoreboard modes
- better typing for list
- write help message

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
                                "list": {
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