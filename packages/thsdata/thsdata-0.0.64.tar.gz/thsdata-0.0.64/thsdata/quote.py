from thsdk import ZhuThsQuote, FuThsQuote, InfoThsQuote, BlockThsQuote
from thsdk.constants import *
import pandas as pd
from datetime import datetime, time
import random
import pytz
import requests
import json
from typing import List, Tuple


def rand_instance(n: int) -> str:
    digits = "0123456789"
    d2 = "123456789"  # d2 used for the first digit to avoid 0 at the start

    if n <= 1:
        return str(random.randint(0, 9))  # Return a single random digit

    # Generate the string with n characters
    result = [random.choice(digits) for _ in range(n)]

    # Ensure the first digit is from d2 (i.e., 1-9)
    result[0] = random.choice(d2)

    return ''.join(result)


def time_2_int(t: datetime) -> int:
    dst = (t.minute +
           (t.hour << 6) +
           (t.day << 11) +
           (t.month << 16) +
           (t.year << 20) -
           0x76c00000)
    return dst


class Quote:
    def __init__(self, ops: dict = None):
        self.ops = ops
        self._zhuQuote = None
        self._fuQuote = None
        self._infoQuote = None
        self._blockQuote = None

    @property
    def zhuQuote(self):
        if self._zhuQuote is None:
            self._zhuQuote = ZhuThsQuote(self.ops)
            self._zhuQuote.connect()
        return self._zhuQuote

    @property
    def fuQuote(self):
        if self._fuQuote is None:
            self._fuQuote = FuThsQuote(self.ops)
            self._fuQuote.connect()
        return self._fuQuote

    @property
    def infoQuote(self):
        if self._infoQuote is None:
            self._infoQuote = InfoThsQuote(self.ops)
            self._infoQuote.connect()
        return self._infoQuote

    @property
    def blockQuote(self):
        if self._blockQuote is None:
            self._blockQuote = BlockThsQuote(self.ops)
            self._blockQuote.connect()
        return self._blockQuote

    def connect(self):
        self.zhuQuote.connect()
        self.fuQuote.connect()
        self.infoQuote.connect()
        self.blockQuote.connect()

    def disconnect(self):
        if self._zhuQuote:
            self._zhuQuote.disconnect()
        if self._fuQuote:
            self._fuQuote.disconnect()
        if self._infoQuote:
            self._infoQuote.disconnect()
        if self._blockQuote:
            self._blockQuote.disconnect()

    def _zhu_query_data(self, req: str):
        try:
            reply = self.zhuQuote.query_data(req)
            if reply.err_code != 0:
                print(f"Query error: {reply.err_code}, Message: {reply.err_message}")
                return pd.DataFrame()  # Return an empty DataFrame on error
            resp = reply.resp
            df = pd.DataFrame(resp.data)
            return df

        except Exception as e:
            print(f"An exception occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on exception

    def _block_data(self, block_id: int):
        try:
            reply = self.blockQuote.get_block_data(block_id)
            if reply.err_code != 0:
                print(f"Query error: {reply.err_code}, Message: {reply.err_message}")
                return pd.DataFrame()  # Return an empty DataFrame on error
            resp = reply.resp
            df = pd.DataFrame(resp.data)
            return df
        except Exception as e:
            print(f"An exception occurred: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on exception

    def _get_block_components(self, block_code: str) -> pd.DataFrame:
        try:
            reply = self.blockQuote.get_block_components(block_code)
            if reply.err_code != 0:
                print(f"Query error: {reply.err_code}, Message: {reply.err_message}")
                return pd.DataFrame()  # Return an empty DataFrame on error
            resp = reply.resp
            df = pd.DataFrame(resp.data)
            return df
        except Exception as e:
            print(f"An exception occurred: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on exception

    def stock_codes(self) -> pd.DataFrame:
        """获取股票市场代码.

        :return: pandas.DataFrame

        Example::

            code        name
            USHA600519  贵州茅台
            USZA300750  宁德时代
            USTM832566    梓橦宫
        """
        return self._block_data(0xC6A6)

    def cbond_codes(self) -> pd.DataFrame:
        """获取可转债市场代码.

        :return: pandas.DataFrame

        Example::

            code        name
            USHD113037   紫银转债
            USZD123158   宙邦转债
            USHD110094   众和转债
        """
        return self._block_data(0xCE14)

    def etf_codes(self) -> pd.DataFrame:
        """获取ETF基金市场代码.

        :return: pandas.DataFrame

        Example::

            code        name
            USHJ589660       综指科创
            USZJ159201   自由现金流ETF
            USHJ510410      资源ETF
        """
        return self._block_data(0xCFF3)

    def security_bars(self, code: str, start: datetime, end: datetime, adjust: str, period: int) -> pd.DataFrame:
        """获取指定证券的K线数据.
        支持日k线、周k线、月k线，以及5分钟、15分钟、30分钟和60分钟k线数据.

        :param code: 证券代码，例如 'USHA600519'
        :type code: str
        :param start: 开始时间，格式为 datetime 对象
        :type start: datetime.datetime
        :param end: 结束时间，格式为 datetime 对象
        :type end: datetime.datetime
        :param adjust: 复权类型， :const:`Fuquanqian`, :const:`Fuquanhou`, :const:`FuquanNo`
        :type adjust: str
        :param period: 数据类型， :const:`Kline1m`, :const:`Kline5m`, :const:`Kline15m`, :const:`Kline30m`, :const:`Kline60m`, :const:`Kline120m`, :const:`KlineDay`, :const:`KlineWeek`, :const:`KlineMoon`, :const:`KlineQuarterly`, :const:`KlineYear`
        :type period: int

        :return: pandas.DataFrame

        Example::

                time    close   volume    turnover     open     high      low
            2024-01-02  1685.01  3215644  5440082500  1715.00  1718.19  1678.10
            2024-01-03  1694.00  2022929  3411400700  1681.11  1695.22  1676.33
            2024-01-04  1669.00  2155107  3603970100  1693.00  1693.00  1662.93
        """
        m_period = {Kline1m, Kline5m, Kline15m, Kline30m, Kline60m, Kline120m}

        if period in m_period:
            start_int = time_2_int(start)
            end_int = time_2_int(end)
        else:
            start_int = int(start.strftime('%Y%m%d'))
            end_int = int(end.strftime('%Y%m%d'))

        reply = self.zhuQuote.security_bars(code, start_int, end_int, adjust, period)
        if reply.err_code != 0:
            print(f"查询错误:{reply.err_code}, 信息:{reply.err_message}")
            return

        resp = reply.resp
        return pd.DataFrame(resp.data)

    def ths_industry_block(self) -> pd.DataFrame:
        """获取同花顺行业板块.

        :return: pandas.DataFrame

        Example::

                      code   name
            0   URFI881165     综合
            1   URFI881171  自动化设备
            2   URFI881118   专用设备
            3   URFI881141     中药
            4   URFI881157     证券
            ..         ...    ...
            85  URFI881138   包装印刷
            86  URFI881121    半导体
            87  URFI881131   白色家电
            88  URFI881273     白酒
            89  URFI881271   IT服务
        """
        return self._block_data(0xCE5F)

    def ths_industry_sub_block(self) -> pd.DataFrame:
        """获取同花顺三级行业板块.

        :return: pandas.DataFrame

        Example::

                       code    name
            0    URFA884270  综合环境治理
            1    URFA884164    自然景点
            2    URFA884065    装饰园林
            3    URFA884161    专业连锁
            4    URFA884068    专业工程
            ..          ...     ...
            225  URFA884091   半导体材料
            226  URFA884160    百货零售
            227  URFA884294    安防设备
            228  URFA884045      氨纶
            229  URFA884095     LED
        """
        return self._block_data(0xc4b5)

    def ths_concept_block(self) -> pd.DataFrame:
        """获取同花顺概念板块.

        :return: pandas.DataFrame

        Example::

                       code       name
            0    URFI885580       足球概念
            1    URFI885758       租售同权
            2    URFI885764      自由贸易港
            3    URFI885760      装配式建筑
            4    URFI885877        转基因
            ..          ...        ...
            391  URFI886037       6G概念
            392  URFI885556         5G
            393  URFI885537       3D打印
            394  URFI886088  2024三季报预增
            395  URFI886097   2024年报预增
        """
        return self._block_data(0xCE5E)

    def ths_block_components(self, block_code: str) -> pd.DataFrame:
        """查询行业，行业三级，概念板块成分股.

        :param block_code: 板块代码，例如 'URFI881157'

        :return: pandas.DataFrame

        Example::

                      code   name
            0   USHA601375  中原证券
            1   USHA601696  中银证券
            2   USHA600030  中信证券
            ..          ...     ...
            46  USZA002939  长城证券
            47  USHA601108  财通证券
            48  USHA600906  财达证券
        """
        return self._get_block_components(block_code)

    def call_auction(self, code: str) -> pd.DataFrame:
        """集合竞价

        :param code: 证券代码，例如 'USHA600519'
        :type code: str

        :return: pandas.DataFrame

        Example::

                                    time    price    bid2_vol    ask2_vol  cur_volume
            0  2025-03-04 09:15:07+08:00  1487.02  2147483648  2147483648         500
            1  2025-03-04 09:15:10+08:00  1487.46         900  2147483648        1100
            2  2025-03-04 09:15:13+08:00  1487.46         997  2147483648        1203
            3  2025-03-04 09:15:16+08:00  1487.46         797  2147483648        1503
            4  2025-03-04 09:15:19+08:00  1487.46         697  2147483648        1603
            ..                       ...      ...         ...         ...         ...
            74 2025-03-04 09:24:46+08:00  1487.00         447  2147483648       11353
            75 2025-03-04 09:24:49+08:00  1487.00          47  2147483648       11953
            76 2025-03-04 09:24:52+08:00  1487.00         147  2147483648       12153
            77 2025-03-04 09:24:55+08:00  1487.00  2147483648         353       12300
            78 2025-03-04 09:24:58+08:00  1485.00  2147483648         253       13100

        """

        now = datetime.now()
        # 使用当前日期，构造当天的 9:15:00 和 9:25:00
        start = datetime.combine(now.date(), time(9, 15, 0))  # 9:15:00
        end = datetime.combine(now.date(), time(9, 25, 0))  # 9:25:00

        # 获取 Unix 时间戳（秒）
        start_unix = int(start.timestamp())
        end_unix = int(end.timestamp())
        market = code[:4]
        short_code = code[4:]
        req = f"id=204&instance={rand_instance(7)}&zipversion=2&code={short_code}&market={market}&datatype=1,10,27,33,49&start={start_unix}&end={end_unix}"

        data = self._zhu_query_data(req)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        data['time'] = pd.to_datetime(data['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(beijing_tz)

        return data

    def wencai(self, condition: str) -> Tuple[List[str], Exception]:
        """问财速查API.

        :param condition: 条件选股
        :return:
        """

        url = "https://eq.10jqka.com.cn/dataQuery/query"

        # 定义请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://eq.10jqka.com.cn/",  # 可选，模拟来源页面
            "Connection": "keep-alive"
        }

        # Prepare query parameters
        params = {"query": condition}

        try:
            # Make HTTP GET request
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for bad status codes

            # Parse JSON response
            data = response.json()

            # Check status_msg
            if data.get("status_msg") != "success":
                return None, Exception(data.get("status_msg"))

            ret = []

            # Get stockList array
            stock_list = data.get("stockList", [])

            # Iterate through stockList
            for item in stock_list:
                stock_code = item.get("stock_code", "")
                market_id = item.get("marketid", "")

                d = stock_code
                if market_id == "17":
                    d = "USHA" + d
                    ret.append(d)
                elif market_id == "21":
                    d = "USHP" + d
                    ret.append(d)
                elif market_id == "22":
                    d = "USHT" + d
                    ret.append(d)
                elif market_id == "33":
                    d = "USZA" + d
                    ret.append(d)
                elif market_id == "37":
                    d = "USZP" + d
                    ret.append(d)
                elif market_id == "151":
                    d = "USTM" + d
                    ret.append(d)
                else:
                    d = "todo" + d
                    print(f"todo market {condition} {d}")

            return ret, None

        except requests.RequestException as e:
            return [], e
        except json.JSONDecodeError as e:
            return [], e
