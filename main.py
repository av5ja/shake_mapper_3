# from ast import List
from multiprocessing.sharedctypes import Value
from numbers import Number
import xml.etree.ElementTree as et
from yaml import SafeLoader
# import yaml.etree.ElementTree as et
import yaml
import matplotlib.pyplot as plt
import os
import sys
import math
import matplotlib
from typing import Optional
from enum import Enum
import xmltodict
from awscli.customizations.cloudformation.yamlhelper import yaml_parse
import re
import json
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString


class WaterLevel(Enum):
    High = "High"
    Mid = "Mid"
    Low = "Low"
    Cmn = "Cmn"
    Sound = "Sound"


class TargetType(Enum):
    Tower = "CoopArrivalPointEnemyTower"
    Twins = "CoopArrivalPointEnemyCupTwins"
    Rocket = "CoopSakerocketJumpPoint"
    Geyser = "CoopSpawnGeyser"
    Artillery = "CoopSakeArtilleryGunPoint"
    Relay = "CoopEventRelayGoldenIkuraDropPoint"
    RelaySpawn = "CoopEventRelaySpawnBoxLocator"
    RelayTornado = "CoopEventRelayTornadoLocator"
    Bank = "CoopIkuraBank"
    Bagman = "CoopSpawnPointSakeFlyBagMan"
    Piller = "CoopSakePillarSpawnPoint"
    PillerArrival = "CoopSakePillarArrivalPoint"
    Enemy = "CoopSpawnPointEnemy"
    Helicopter = "CoopHelicopterCenterPoint"
    VSGeyser = "CoopVSStageGeyser"
    BoxLocator = "CoopSpawnBoxLocator"
    Diver = "CoopSakeDiverNoDiveArea"
    TwinsRail = "CoopCupTwinsRail"
    PatrolRail = "CoopEnemyPatrolRail"
    SakeCariierRail = "CoopSakeCarrierRail"
    GiantNoJumpArea = "CoopSakelienGiantNoJumpArea"
    PathArea = "CoopPathCorrectArea"
    PathPoint = "CoopPathCorrectPoint"


class Position:
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]

    def __init__(self, object: dict):
        translates = object.get("Translate")
        if translates != None:
            self.x = float(translates[0]) * 10
            self.y = float(translates[2]) * 10
            self.z = float(translates[1]) * 10
        else:
            self.x = None
            self.y = None
            self.z = None


class CoopObject:
    name: str
    position: Position
    water_level: WaterLevel

    def __init__(self, object: dict):
        # オブジェクト名
        self.name = object["Gyaml"]
        # 潮位
        self.water_level = WaterLevel(
            object["Layer"]
        )
        # 座標
        self.position = Position(object)


def objects(object: dict) -> list[CoopObject]:
    elements: list[CoopObject] = list(
        map(lambda x: CoopObject(x), object["root"]["Actors"])
    )
    # オブジェクト名ごとにソートする
    elements.sort(key=lambda x: x.name)
    return elements


def color(obj: CoopObject) -> str:
    if obj.water_level == WaterLevel.High:
        return "yellowgreen"
    if obj.water_level == WaterLevel.Mid:
        return "deepskyblue"
    if obj.water_level == WaterLevel.Low:
        return "tomato"
    if obj.water_level == WaterLevel.Cmn:
        return "blueviolet"


def marker(obj: CoopObject) -> str:
    try:
        if int(obj.name[-1]) == 0:
            return "o"
        if int(obj.name[-1]) == 1:
            return "v"
        if int(obj.name[-1]) == 2:
            return "^"
    except ValueError:
        return "o"


def plot(objects: list[CoopObject], name: str):
    if os.path.exists(f"outputs/{name}") == False:
        os.mkdir(f"outputs/{name}")
    for target in TargetType:
        # プロットの初期化
        plt.xlim([900, -900])
        plt.ylim([-900, 900])
        plt.figure(figsize=(4, 4))
        plt.gca().set_aspect("equal")

        for water_level in WaterLevel:
            # コンテナの位置は常に表示する
            banks = list(filter(lambda x: x.name == "CoopIkuraBank", objects))
            for bank in banks:
                plt.scatter(bank.position.x, bank.position.y, c="yellow", marker="s")

            elements: list[CoopObject] = list(
                filter(
                    lambda x: x.water_level == water_level and target.value in x.name,
                    objects,
                )
            )
            print(water_level, target.value, len(elements))
            for object in elements:
                plt.scatter(
                    object.position.x,
                    object.position.y,
                    c=color(object),
                    marker=marker(object),
                )
        plt.tick_params(
            labelbottom=False,
            labelleft=False,
            labelright=False,
            labeltop=False,
            bottom=False,
            left=False,
            right=False,
            top=False,
        )
        try:
            plt.savefig(
                f"outputs/{name}/{target.value}.png",
                dpi=300,
                transparent=True,
                bbox_inches="tight",
                pad_inches=0.0,
            )
            plt.close()
        except SystemError:
            print("SystemError")


if __name__ == "__main__":
    print("ShakeMapper for Splatoon 3")
    print("Developed by @tkgling")

    files = os.listdir("yamls")
    for file in files:
        if "bcett.yaml" in file:
            path = f"yamls/{file}"
            name = os.path.splitext(file)[0]
            # 余計な短縮表現を省略する
            yaml_str: str = re.sub("!u|!l", "", open(path, "r", encoding="utf-8").read())
            yaml_dict: dict = yaml.safe_load(yaml_str)
            plot(objects(yaml_dict), name)