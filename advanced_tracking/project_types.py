from typing import Dict, List, Literal
from mcdreforged.api.all import Serializable

BlockTypeMode = Literal["whitelist", "blacklist", None]

class BlockTypes(Serializable):
    mode:BlockTypeMode = None
    list:Dict[str, List[Dict[str, str|bool|int]]] = {}


if __name__ == "__main__":
    blockTypes = BlockTypes(
        mode=None, list={
            "list": {
                "smooth_stone_slab": [
                    {"type":"bottom"},
                    {"type":"top", "waterlogged":True}
                ]
            },
            "mode": "blacklist"
        }
    )
    print(blockTypes.serialize())