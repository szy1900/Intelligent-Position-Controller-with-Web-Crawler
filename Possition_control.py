from selenium import webdriver
import tushare as ts
import datetime
from fake_useragent import UserAgent
from lxml import etree
import pandas as pd
import numpy as np
import requests
import traceback
import os
import ta


class Position_control(object):
    def __init__(self, pro, today):
        self.pro = pro
        self.sh_file_name = 'SH_index_infor' + today + '.csv'
        self.cyb_file_name = 'CYB_index_infor' + today + '.csv'

    def compute_index_variation(self):
        if not os.path.exists(self.sh_file_name):
            My_pos.get_sh_index()
            print('SH index data is updated')
        if not os.path.exists(self.cyb_file_name):
            My_pos.get_cyb_index()
            print('CYB index data is updated')
        try:
            sh_index_data = pd.read_csv(self.sh_file_name, encoding='gbk')
            cyb_index_data = pd.read_csv(self.cyb_file_name, encoding='gbk')
            sh_index_data = self.atr_index(sh_index_data)
            cyb_index_data = self.atr_index(cyb_index_data)
            position_sh = 0.5/(sh_index_data['atr']-0.4)*100
            position_cyb = 0.5/(cyb_index_data['atr']-0.4)*100-1
            # if sh_index_data['price'][0]< sh_index_data['price'].mean():
            #     Total_position = 10
            # else:
            Total_position = position_sh +position_cyb
            print(Total_position)
        except Exception:
            traceback.print_exc()

    def atr_index(self, df, n=5):
        data = df.copy()
        data['yesterday_close'] = df['price'].shift(-1)
        data.dropna(0, inplace=True)
        high = data['high'].map(self.con)
        low = data['low'].map(self.con)
        price = data['price'].map(self.con)
        yesterday_close = data['yesterday_close'].map(self.con)
        data['tr0'] = abs(high - low)
        data['tr1'] = abs(high - yesterday_close)
        data['tr2'] = abs(low - yesterday_close)
        tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        tr_reverse = tr.reindex(index=data.index[::-1])
        atr = tr_reverse.ewm(span=n, adjust=False, min_periods=n).mean()
        df['atr'] = atr.reindex(index=data.index[::-1])/price*100
        # atr2 = ta.volatility.AverageTrueRange(high = high.reindex(index=data.index[::-1]),low = low.reindex(index=data.index[::-1]) ,close= yesterday_close.reindex(index=data.index[::-1]), n = 5)
        return df

    def wwma(self, values, n):
        """
         J. Welles Wilder's EMA
        """
        return values.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()

    def con(self, column):
        column = column.replace(',', '')
        column = float(column)
        return column

    def get_sh_index(self):
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        url = 'https://cn.investing.com/indices/shanghai-composite-historical-data'
        html = requests.get(url=url, headers=headers).text
        p = etree.HTML(html)
        keys = p.xpath('//*[@id="curr_table"]/thead/tr/th/@data-col-name')

        xpath = '//*[@id="curr_table"]/tbody/tr/td/text()'
        values = p.xpath(xpath)
        values = np.array(values).reshape(-1, 7)
        df = pd.DataFrame(data=values, columns=keys)
        df.to_csv(self.sh_file_name, encoding='gbk')
        return df

    def get_cyb_index(self):
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        url = 'https://cn.investing.com/indices/chinext-price-historical-data'
        html = requests.get(url=url, headers=headers).text
        p = etree.HTML(html)
        keys = p.xpath('//*[@id="curr_table"]/thead/tr/th/@data-col-name')

        xpath = '//*[@id="curr_table"]/tbody/tr/td/text()'
        values = p.xpath(xpath)
        values = np.array(values).reshape(-1, 7)
        df = pd.DataFrame(data=values, columns=keys)
        df.to_csv(self.cyb_file_name, encoding='gbk')

    def maximal_allowed_position(self):
        pass

    def run(self):
        self.compute_index_variation()


if __name__ == '__main__':
    ts.set_token('631237e6e4485179e8fe3627eaff34f59a625bf2b8419a8cb507e561')
    pro = ts.pro_api()
    today = datetime.date.today()
    today = today.strftime('%Y%m%d')
    # df = ts.get_index()
    # df = pro.daily(ts_code='000001.SZ', start_date='20190701', end_date='20200306')

    My_pos = Position_control(pro, today=today)
    My_pos.run()
    # today = datetime.date.today()
    #
    #
    #
    # #
    #
    #
    #
    # print(df)
    #
    # browser = webdriver.Chrome()
    # browser.get('http://www.baidu.com/')
    # kw = browser.find_element_by_xpath('//*[@id="kw"]')
    # kw.send_keys('赵丽颖')
    # su = browser.find_element_by_xpath('//*[@id="su"]')
    # su.click()

# https://hq.sinajs.cn/rn=1583486231337&list=sz002161,sz002161_i,bk_new_dzxx
