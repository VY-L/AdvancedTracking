# AdvancedTracking
MCDR plugin used to track customary player events

[English](README.md) | **中文**


## 特性

1. 用 carpetscript 跟踪自定义的玩家行为
   - 行为
     - [x] 方块放置
     - [x] 方块破坏
     - [ ] 非挂机行为
   - 自定义限制
     - [x] 范围（由于scarpet限制，基于玩家位置）
     - [x] 方块类型（可自定义含水等属性限制）
     - [ ] 玩家ID/玩家状态
2. 基于
   - [x] 权重求和
3. 用MCDR作为用户交互管理追踪器和计分板


## 用法

### 理解结构

这个插件就是管理两类东西：计分板和追踪器

计分板永远对应游戏内的计分板目标，目前只有一个模式：对多个追踪器的加权求和。每个计分板都有以下属性：目标名，显示名称，追踪器和其权重形成的键值对

追踪器就是追踪玩家的行为，为了(我也不知道有没有意义)优化，可以给他们分组。每个跟踪器都属于几个类型，目前只实现了两个：玩家破坏方块和放置方块。每个跟踪器拥有以下属性：一个ID，一个范围(又是为了优化，不写反正肯定没问题)，以及一些组件。每个组件，又都有一个范围(这个是重要的)，一个方块类型过滤器，即一个白名单或者黑名单，决定破坏哪些方块才算，白名单黑名单也可以记录特定的方块状态(比如说含水与否)，具体请看data schemes。

以一个需要空置域的机器为例，我可以有一个挖沟的追踪器，旗下四个组件，分别为东南西北沟，因为范围只能是长方体；另外，我们还可以有个挖黑曜石的追踪器，一个机器范围内放置方块的追踪器，和一个装饰范围防止方块的追踪器。

接下来，我们可以为每个追踪器都创建一个计分板，另外再按照权重设置一个总计分板，记录所有玩家对一个项目的贡献

对于很多这种重复的形式，我会实现一些“预设”。比如说，会有一个对于挖沟的预设，用户只需要输入空置域的两个对角即可自动生成一个带有4个组件的跟踪器。(实现之后)这也会是推荐的创建计分板的方式。


### 命令

基础: `!!at`

`!!at` 进入基于点击聊天栏超链接的UI（鸽）

`!!at help` 查看帮助

`!!at add tracker <tracker_name> <tracker_type>` 创建新的空跟踪器

`!!at add tracker <tracker_name> <preset_name> ...` 用一个预设创建一个跟踪器

`!!at add tracker <tracker_name> preset <preset_name> ...` 用预设创建跟踪器（未来支持自己写预设可能只能用这个

`!!at tracker <tracker_name> add <component_name>` 在一个跟踪器下创建一个组件

`!!at tracker <tracker_name> <component_name> create` 同理

`!!ad add component <tracker_name> <component_name>` 同理

`!!at tracker <tracker_name> delete/remove` 删除一个跟踪器，注：数据也会删掉，需要 `!!at confirm`

`!!at component <tracker_name> <component_name> area single <attr> <value>` 更改组件范围的一个属性(比如说把最小x值设成-1000，或者设为null(不在乎))

`!!at component <tracker_name> <component_name> cuboid <x1> <y1> <z1> <x2> <y2> <z2>` 按照一个长方体的两角覆写一个组件的范围

`!!at component <tracker_name> <component_name> rectangle <x1> <z1> <x2> <z2>`按照一个长方型的两角覆写一个组件的范围（不在意y值）

`!!at component <tracker_name> <component_name> blacklist set <blacklist>` 覆写一个组件的黑名单

`!!at component <tracker_name> <component_name> whitelist set <whitelist>`...

`!!at component <tracker_name> <component_name> blacklist add <instance>` 在一个组件的黑名单中加入一个方块

`!!at component <tracker_name> <component_name> whitelist add <instance>`...

`!!at component <tracker_name> <component_name> blacklist` 设置为黑名单模式

`!!at component <tracker_name> <component_name> whitelist`

`!!at component <tracker_name> <component_name> remove/delete`

`!!at tracker <tracker_name> remove/delete <component_name>`


`!!at add scoreboard <scoreboard_name>`

`!!at add scoreboard <scoreboard_name> <"Display Name">`

`!!at add scoreboard <scoreboard_name> <"Display Name"> <tracker_name>` 为一个跟踪器创建一个单独的计分板

`!!at scoreboard <scoreboard_name> preset <preset_name>` 用预设创建/覆写计分板

`!!at scoreboard add <scoreboard_name> <tracker_name> <weight>` 在一个计分板下面增加一个计分板-权重对


## Other TODOs
- Lang
- Usages, How It works in README.md
- Variable update mechanisms
- add type for Area, BlockType
- 禁用

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