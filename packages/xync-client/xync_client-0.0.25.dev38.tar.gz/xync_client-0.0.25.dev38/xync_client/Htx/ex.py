from asyncio import run

from x_model import init_db
from xync_schema import models, types
from xync_schema.models import Ex, Cur
from xync_schema.enums import PmType

from xync_client.Abc.Ex import BaseExClient
from xync_client.Htx.pyd.types import Country
from xync_client.loader import PG_DSN


class ExClient(BaseExClient):
    # 20: Get all pms
    async def pms(self, _cur: Cur = None) -> dict[int, types.Pm]:
        dist = {
            0: PmType.card,
            1: PmType.bank,
            2: PmType.cash,
            3: PmType.emoney,
            4: PmType.emoney,
            5: PmType.IFSC,
        }

        pms = (await self._coin_curs_pms())["payMethod"]

        pmsd = {
            pm["payMethodId"]: types.Pm(
                id=pm["payMethodId"],
                name=pm["name"],
                type_=dist.get(pm["template"], pm["template"]),
                logo=pm.get("bankImage", pm["bankImageWeb"]),
            )
            for pm in pms
        }

        return pmsd

    # 21: Get all: currency,pay,allCountry,coin
    async def curs(self) -> list[types.CurE]:
        res = (await self._coin_curs_pms())["currency"]
        return [
            types.CurE(exid=c["currencyId"], ticker=c["nameShort"]) for c in res
        ]  # if c['showPtoP'] todo: wht "showPtoP" is means

    # 22: Список платежных методов по каждой валюте
    async def cur_pms_map(self) -> dict[int, set[int]]:
        res = await self._coin_curs_pms()
        wrong_pms = {4, 34, 498, 548, 20009, 20010}  # , 212, 239, 363  # these ids not exist in pms
        return {c["currencyId"]: set(c["supportPayments"]) - wrong_pms for c in res["currency"] if c["supportPayments"]}

    # 23: Список торгуемых монет
    async def coins(self) -> list[types.CoinE]:
        coins: list[dict] = (await self._coin_curs_pms())["coin"]
        return [types.CoinE(exid=c["coinId"], ticker=c["coinCode"]) for c in coins if c["coinType"] == 2]

    # 99: Страны
    async def countries(self) -> list[Country]:
        res = await self._coin_curs_pms()
        cts = [
            Country(
                id=c["countryId"],
                code=c["code"],
                name=c["name"],
                short=c["appShort"],
                cur_id=c["currencyId"],
            )
            for c in res["country"]
        ]
        return cts

    # Get all: currency,pay,allCountry,coin
    async def _coin_curs_pms(self) -> (dict, dict, dict, dict):
        res = (await self._get("/-/x/otc/v1/data/config-list?type=currency,pay,coin,allCountry"))["data"]
        res["currency"][0]["currencyId"] = 1
        [c.update({"currencyId": 1, "name": ""}) for c in res["country"] if c["currencyId"] == 172]
        return res


async def main():
    _ = await init_db(PG_DSN, models, True)
    ex = await Ex.get(name="Htx")
    cl = ExClient(ex)
    await cl.set_pmcurexs()
    await cl.set_coinexs()
    await cl.close()


if __name__ == "__main__":
    run(main())
