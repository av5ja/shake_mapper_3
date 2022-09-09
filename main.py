# from ast import List
from multiprocessing.sharedctypes import Value
from numbers import Number
import xml.etree.ElementTree as et
import matplotlib.pyplot as plt
import os
import sys
import math
import matplotlib
from typing import Optional
from enum import Enum

class WaterLevel(Enum):
  High = 'High'
  Mid = 'Mid'
  Low = 'Low'
  Cmn = 'Cmn'
  Sound = 'Sound'

class TargetType(Enum):
  Tower = 'CoopArrivalPointEnemyTower'
  Twins = 'CoopArrivalPointEnemyCupTwins'
  Rocket = 'CoopSakerocketJumpPoint'
  Geyser = 'CoopSpawnGeyser'
  Artillery = 'CoopSakeArtilleryGunPoint'
  Relay = 'CoopEventRelayGoldenIkuraDropPoint'
  RelaySpawn = 'CoopEventRelaySpawnBoxLocator'
  RelayTornado = 'CoopEventRelayTornadoLocator'
  Bank = 'CoopIkuraBank'
  Bagman = 'CoopSpawnPointSakeFlyBagMan'
  Piller = 'CoopSakePillarSpawnPoint'
  PillerArrival = 'CoopSakePillarArrivalPoint'
  Enemy = 'CoopSpawnPointEnemy'
  Helicopter = 'CoopHelicopterCenterPoint'

class Position:
  x: Optional[float]
  y: Optional[float]
  z: Optional[float]

  def __init__(self, element: et.Element):
    translates = element.findall("C0/[@Name='Translate']/D2")
    if len(translates) != 0:
      self.x = float(translates[0].attrib['StringValue']) * 10
      self.y = float(translates[2].attrib['StringValue']) * 10
      self.z = float(translates[1].attrib['StringValue']) * 10
    else:
      self.x = None 
      self.y = None 
      self.z = None 

class CoopObject:
  name: str
  position: Position
  water_level: WaterLevel

  def __init__(self, element: et.Element):
    # オブジェクト名
    self.name = element.find("A0/[@Name='Gyaml']").attrib['StringValue']
    # 潮位
    self.water_level = WaterLevel(element.find("A0/[@Name='Layer']").attrib['StringValue'])
    # 座標
    self.position = Position(element)


def objects(xml: et.ElementTree) -> list[CoopObject]:
  elements: list[CoopObject] = list(map(lambda x: CoopObject(x), xml.findall("C1/C0/[@Name='Actors']/C1")))

  # オブジェクト名ごとにソートする
  elements.sort(key=lambda x: x.name)
  return elements

def color(obj: CoopObject) -> str:
  if obj.water_level == WaterLevel.High:
    return 'green'
  if obj.water_level == WaterLevel.Mid:
    return 'blue'
  if obj.water_level == WaterLevel.Low:
    return 'red'
  if obj.water_level == WaterLevel.Cmn:
    return 'black'

def marker(obj: CoopObject) -> str:
  try:
    if int(obj.name[-1]) == 0:
      return 'o'
    if int(obj.name[-1]) == 1:
      return 'v'
    if int(obj.name[-1]) == 2:
      return '^'
  except ValueError:
    return 'o'

def plot(objects: list[CoopObject], name: str):
  if os.path.exists(f"outputs/{name}") == False:
    os.mkdir(f"outputs/{name}")
  for target in TargetType:
    # プロットの初期化
    plt.xlim([800, -800])
    plt.ylim([-800, 800])
    
    for water_level in WaterLevel:
      # Cmnはどうせ使わないので無視
      if water_level == WaterLevel.Cmn:
        continue
     
      # コンテナの位置は常に表示する
      banks = list(filter(lambda x: x.name == 'CoopIkuraBank', objects))
      for bank in banks:
        plt.scatter(bank.position.x, bank.position.y, c='yellow', marker="s")
      
      elements: list[CoopObject] = list(filter(lambda x: x.water_level == water_level and target.value in x.name, objects))
      print(target.value, len(elements))
      for object in elements:
        plt.scatter(object.position.x, object.position.y, c=color(object), marker=marker(object))
    plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)
    plt.savefig(f"outputs/{name}/{target.value}.png", dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.0)
    plt.close()


if __name__ == "__main__":
  print("ShakeMapper for Splatoon 3")
  print("Developed by @tkgling")

  files = os.listdir("xmls")
  
  for file in files:
    path = f"xmls/{file}"
    name = os.path.splitext(file)[0]
    
    xmlp = et.XMLParser(encoding='utf-8')
    xml = et.parse(path, parser=xmlp)
    plot(objects(xml), name)
