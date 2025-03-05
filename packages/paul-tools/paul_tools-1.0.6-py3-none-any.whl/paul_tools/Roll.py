"""
骰子擲點模塊

這個模塊提供了進行各種骰子擲點的功能，支持:
- 標準骰子擲點 (例如 1d6, 2d20)
- DND規則判定
- COC規則判定
- 自定義列表隨機選擇

主要類:
- Roll: 骰子擲點的核心類
- RollType: 擲點類型枚舉
- returnType: 擲點結果類型枚舉
"""

import re
import time
from enum import Enum
from pathlib import Path
from random import Random
from typing import TypedDict, TypeVar

from .__init__ import logger
from .I18n import I18n
from .Tools import color

__all__ = [
    "Roll",
    "RollType",
    "returnType",
    "RollNumReturnType",
    "RollNumReturnValueType",
]


T = TypeVar("T")


class RollType(Enum):
    """擲點類型枚舉

    用於定義不同的擲點規則系統。

    屬性:
        NONE: 無特殊規則的普通擲點
        DND: DND規則系統的擲點
        COC: 克蘇魯的呼喚規則系統的擲點
    """

    NONE = 0

    DND = 1
    COC = 2


class returnType(Enum):
    """擲點結果類型枚舉

    定義擲點的結果等級。

    屬性:
        BigNotSuccess: 大失敗 (-2)
        notSuccess: 失敗 (-1)
        NONE: 普通結果 (0)
        success: 成功 (1)
        BigSuccess: 大成功 (2)
    """

    BigNotSuccess = -2
    notSuccess = -1
    NONE = 0
    success = 1
    BigSuccess = 2


class RollNumReturnValueType(TypedDict):
    Value: int
    msg: str | None
    RollValueClass: returnType


class RollNumReturnType(TypedDict):
    rollValueList: list[int]
    Type: RollType
    returnValueList: list[RollNumReturnValueType]


class RollNumRegToolsReturnType(TypedDict):
    xD: int
    Dy: int
    sumBonus: int


class Roll:
    """骰子擲點核心類

    提供各種骰子擲點相關的功能，包括:
    - 解析擲點指令
    - 執行擲點
    - 判定成功失敗
    - 計算期望值

    屬性:
        debug (bool): 是否開啟調試模式
        rollType (RollType): 使用的擲點規則類型
        logSum (bool): 是否記錄總和
        isLog (bool): 是否輸出日誌
        seed: 隨機數種子值
    """

    rollNumTextStructureSet: set[re.Pattern[str]] = {
        re.compile(r"(\d*)(d|D)(\d+)(( +)?((\+|\-)(\d+)))?")
    }
    """
```ebnf
ao = ( '+' | '-' );
digit = ( '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' );
number = [ ao ], { digit };
rollText = [ number ], ( 'd' | 'D' ), number, [ ao, number ];
```
"""

    @staticmethod
    def rollTextReplace(text: str) -> str:
        isReplace: bool = True
        rText = text
        match text.lower():
            case "int" | "intelligence":
                rText = "智力"
            case "san" | "sanity":
                rText = "理智"
            case _:
                isReplace = False
        rText += " " if isReplace else ""
        logger.debug(f"rollTextReplace({repr(text)}) -> {repr(rText)}")
        return rText

    def __init__(
        self,
        debug: bool = False,
        rollType: RollType = RollType.NONE,
        logSum: bool = True,
        isLog: bool = True,
        seed: int | float | str | bytes | bytearray = time.time(),
    ) -> None:
        self.debug = debug
        self.rollType = rollType
        self.logSum = logSum
        self.isLog = isLog
        self.__seed = seed

        self.__i18n_obj = I18n(
            dirRoot=str(Path(__file__).parent),
            langJson={
                "en_us": {
                    "updata": "2024/5/24 12:56 UTC+8",
                    "any": "{}",
                    "file_lang": "en_us",
                    "paul_tools__Roll__Roll__Exception__rollText_Not_Match_The_Structure": "rollText will not ben {},will ben {}.",
                },
                "zh_hk": {
                    "updata": "2024/5/24 12:56 UTC+8",
                    "any": "{}",
                    "file_lang": "zh_hk",
                    "paul_tools__Roll__Roll__Exception__rollText_Not_Match_The_Structure": "rollText 不是{}，而是{}。",
                },
            },
        )
        self.__random_obj = Random()
        self.__random_obj.seed(self.__seed)
        logger.debug(f"random.seed: {self.seed}")

    @property
    def seed(self) -> int | float | str | bytes | bytearray:
        return self.__seed

    @seed.setter
    def seed(self, seed: int | float | str | bytes | bytearray) -> None:
        self.__seed = seed
        self.__random_obj.seed(self.__seed)
        logger.debug(f"set seed={self.__seed}")

    @staticmethod
    def RollNumTextToDataTools(rollText: str) -> RollNumRegToolsReturnType:
        """解析擲點指令文本

        將形如 "1d20+5" 的擲點指令解析為可用的數值參數

        參數:
            rollText: 擲點指令文本，例如 "2d6+3"

        返回:
            包含 [擲點次數, 骰子面數, 加值] 的列表

        異常:
            Exception: 當指令格式不符合規範時拋出
        """
        rollData: list[str] | None = None
        userReg = None
        for rollTextStructure in Roll.rollNumTextStructureSet:
            if (tmp1 := re.search(rollTextStructure, rollText)) is None:
                continue
            userReg = rollTextStructure
            rollData = [tmp1.group(1), tmp1.group(3), tmp1.group(6)]
            break
        if rollData is None or len(rollData) != 3:
            raise Exception
        else:
            logger.debug(f"RollNumRegTools({repr(rollText)})--{userReg=}")

        if rollData[0] == "":
            rollData[0] = "1"
        intRollData: list[int] = []
        if rollData[2] is None:
            rollData[2] = "0"
        for tmp1 in rollData:
            intRollData.append(int(tmp1))
        logger.debug(f"RollNumRegTools({repr(rollText)})--{userReg=}-{intRollData=}")
        return {
            "xD": intRollData[0],
            "Dy": intRollData[1],
            "sumBonus": intRollData[2],
        }

    def RollNum(
        self,
        rollData: RollNumRegToolsReturnType | None = None,
        *,
        xD: int | None = None,
        Dy: int | None = None,
        sumBonus: int = 0,
        bonus: int = 0,
        success: int | None = None,
        whyJudged: str = "",
    ) -> RollNumReturnType:
        """執行骰子擲點並進行結果判定

        支援:
        - 基礎擲點計算
        - 成功/失敗判定
        - 大成功/大失敗判定
        - 結果統計和輸出

        參數:
            xD (int): 擲點次數
            Dy (int): 骰子面數
            sumBonus (int): 總結果加值
            bonus (int): 每次擲點加值
            success (int): 成功判定閾值
            whyJudged (str): 擲點原因說明

        返回:
            包含擲點結果的字典，包括:
            - rollValueList: 擲點結果列表
            - Type: 擲點類型
            - returnValueList: 詳細結果列表
        """
        if rollData:
            xD, Dy, sumBonus = rollData["xD"], rollData["Dy"], rollData["sumBonus"]

        if Dy is None:
            logger.warning("Dy is None and rollData is None")
            raise ValueError("Dy is None and rollData is None")

        if xD is None:
            xD = 1
        rollValueList: list[int] = []
        returnValueList: list[RollNumReturnValueType] = []
        whyJudged = self.rollTextReplace(whyJudged)

        logger.debug(f"rollIntData: {xD}d{Dy}")

        if self.isLog:
            print("=" * 20)
            _ = f" {success=}" if success is not None else ""
            print(f"Roll:> {whyJudged}({xD}d{Dy} {sumBonus:+}){_}")
            del _

        # 擲骰
        for i in range(xD):
            _i = i + 1
            rollValue = self.__random_obj.randint(1, Dy)
            trueRollValue = rollValue + bonus

            ####
            # #tag DEBUG for debug
            # rollValue = 19
            # trueRollValue = rollValue+bonus
            ####

            addMsg: str = ""
            printColor: str = ""
            RollValueClass = returnType.NONE
            if self.rollType != RollType.NONE:
                if success is not None:
                    if self.rollType == RollType.DND:
                        if trueRollValue >= success:
                            addMsg = f" [{whyJudged}成功]"
                            printColor = "GREEN"
                            RollValueClass = returnType.success
                        elif trueRollValue < success:
                            addMsg = f" [{whyJudged}失敗]"
                            printColor = "RED"
                            RollValueClass = returnType.notSuccess
                    elif self.rollType == RollType.COC:
                        if trueRollValue < success:
                            addMsg = f" [{whyJudged}成功]"
                            printColor = "GREEN"
                            RollValueClass = returnType.success
                        else:
                            addMsg = f" [{whyJudged}失敗]"
                            printColor = "RED"
                            RollValueClass = returnType.notSuccess
                if self.rollType == RollType.DND and Dy == 20:
                    if rollValue == 20:
                        addMsg = f" [{whyJudged}大成功!]"
                        printColor = "LIGHTGREEN_EX"
                        RollValueClass = returnType.BigSuccess
                    elif rollValue == 1:
                        addMsg = f" [{whyJudged}大失敗!]"
                        printColor = "LIGHTRED_EX"
                        RollValueClass = returnType.BigNotSuccess
                if self.rollType == RollType.COC and Dy == 100:
                    if rollValue == 0:
                        addMsg = f" [{whyJudged}大成功!]"
                        printColor = "LIGHTGREEN_EX"
                        RollValueClass = returnType.BigSuccess
                    elif rollValue == 100:
                        addMsg = f" [{whyJudged}大失敗!]"
                        printColor = "LIGHTRED_EX"
                        RollValueClass = returnType.BigNotSuccess
            msg: str | None = None
            if self.isLog:
                msgBonus = ""
                if bonus != 0:
                    msgBonus: str = str(bonus)
                    if msgBonus[0] != "-":
                        msgBonus = "+" + msgBonus
                    msgBonus += f" = {trueRollValue}"

                msg = f"   {xD}d{Dy}:[{_i:>{len(str(xD))}}] = {rollValue:>0{len(str(Dy))}} {msgBonus}{addMsg}"

                print(*color(msg, color=printColor))

            returnValueList.append(
                {"Value": trueRollValue, "msg": msg, "RollValueClass": RollValueClass}
            )
            rollValueList.append(trueRollValue)
            if self.debug:
                print(("rollValueList: ", rollValueList))

        if self.isLog:
            _ = sum(rollValueList)
            msgSumBonus = ""
            if sumBonus != 0:
                msgSumBonus = str(sumBonus)
                if msgSumBonus[0] != "-":
                    msgSumBonus = "+" + msgSumBonus
                msgSumBonus = " " + msgSumBonus
                msgSumBonus += f" = {_ + sumBonus}"
            if self.logSum:
                print(f"sum = {_}{msgSumBonus}")
            print(f"X̄ = {_ / len(rollValueList):.2f}")
            print("=" * 20)

        return {
            "rollValueList": rollValueList,
            "Type": self.rollType,
            "returnValueList": returnValueList,
        }

    def RollList(self, rollList: list[T], *, whyJudged: str = "") -> T:
        """RollList 的 Docstring

        :param self: 說明
        :type self:
        :param rollList: 說明
        :type rollList:
        :param whyJudged: 說明
        :type whyJudged: str
        :return: 說明
        :rtype: Any"""
        r: T = self.__random_obj.choice(rollList)
        if self.debug:
            print("rollValue: ", r)
        if self.isLog:
            print("=" * 20)
            print(f"Roll List:> {whyJudged}({' '.join(map(str, rollList))})")
            print(f"    r={r}")
            print("=" * 20)
        return r

    def getExpectedValue(
        self, values: list[int] | list[float], probabilities: list[float]
    ) -> float:
        """計算期望值

        根據給定的值和對應概率計算期望值。

        參數:
            values: 可能的值列表
            probabilities: 對應的概率列表

        返回:
            計算出的期望值

        異常:
            ValueError: 當參數不合法時拋出
        """
        # 檢查 values 和 probabilities 的長度是否相等
        if len(values) != len(probabilities):
            raise ValueError("values 與 probabilities 長度不等。")

        # 確保概率之和為 1
        total_probability: float = sum(probabilities)
        if not (0.99 <= total_probability <= 1.01):  # 使用範圍來考慮浮點數誤差
            raise ValueError("概率之和並不等於 1，請檢查概率分配。")

        # 計算期望值
        expected_value: float = sum(v * p for v, p in zip(values, probabilities))
        return expected_value
