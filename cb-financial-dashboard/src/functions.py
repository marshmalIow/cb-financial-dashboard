from requests import get, session  # библиотека для отправки запросов
from bs4 import BeautifulSoup #библиотека которая из необработанного HTML кода страницы создает структурированный массив данных
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
import threading


Year_start = 2023
thread_local = threading.local()
Bank_name = ''

def write_to_csv(assets,date, liabilities):
    assets = decoder(assets)
    str_ = str(date)+ 'assetsres.csv'
    assets.to_csv(str_)
    liabilities = decoder(liabilities)

    liabilities.to_csv(str_, mode = 'a')

def parser(page_link):
    global Bank_name
    session = requests.Session()
    dfs = {}
    #page_link = 'https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1027739053704'
    responce = session.get(page_link)
    soap = BeautifulSoup(responce.content, 'html.parser')

    Bank_name = soap.find('span', class_ ="referenceable").get_text().split(' ',1)[1]

    def get_link(year, session):

        x_101 = soap.find('div', {'data-versions-items': year})
        x_102 = x_101.find_next('div', {'data-versions-items': year})
        x_123 = x_102.find_next('div', {'data-versions-items': year})
        x_135 = x_123.find_next('div', {'data-versions-items': year})
        links = {}
        def add_link(d, idx, link):
            if d not in links:
                links[d] = [None, None, None, None]
            links[d][idx] = link

        try:
            for item in x_101.find_all('a'):
                l = item.get('href')
                d = pd.to_datetime(l.split('=')[-1])
                add_link(d,0,l)


            for item in x_102.find_all('a'):
                l = item.get('href')
                d = pd.to_datetime(l.split('=')[-1])
                add_link(d,1,l)

            for item in x_123.find_all('a'):
                l = item.get('href')
                d = pd.to_datetime(l.split('=')[-1])
                add_link(d,2,l)

            for item in x_135.find_all('a'):
                l = item.get('href')
                d = pd.to_datetime(l.split('=')[-1])
                add_link(d,3,l)


        except:
            df = None

        return links

    for year in range(2026,Year_start,-1):
        df = get_link(year,session)
        if df is not None:
            dfs.update(df)

    res = pd.DataFrame.from_dict(dfs, orient='index').reset_index()
    res.columns = ['date','f101','f102','f123','f135']
    #res.date = res.date.dt.to_period('M')

    res = res.sort_values(by='date').reset_index(drop = 'True')

    return(res)



def get_data_from_101(date,link,thread_local):

    cb = 'https://www.cbr.ru'
    aa = 'https://www.cbr.ru/banking_sector/credit/coinfo/f101?regnum=1481&dt=2025-01-01'
    responce = thread_local.get((cb + link))
    #responce = get(aa)
    soap = BeautifulSoup(responce.content, 'html.parser')

    x = soap.find_all('tr')[5:]
    ass = []
    liab = []
    flag = True
    count = 0
    for row in x:
        if 'italic' in row.get('class', []):
            if count == 0:
                ass.append([
                    item.get_text(strip=True).replace('\xa0', '')
                    for item in row.find_all('td')
                    if item.get_text(strip=True)])

            if count == 1:
                liab.append([
                    item.get_text(strip=True).replace('\xa0', '')
                    for item in row.find_all('td')
                    if item.get_text(strip=True)])
            count += 1
            continue

        if count == 0:
            ass.append([
                item.get_text(strip=True).replace('\xa0', '')
                for item in row.find_all('td')
                if item.get_text(strip=True)])
            continue

        if count == 1:
            liab.append([
                item.get_text(strip=True).replace('\xa0', '')
                for item in row.find_all('td')
                if item.get_text(strip=True)])
            continue

        else:
            break

    assets = pd.DataFrame(ass)
    if assets.shape[1] != 3:
        print("BAD ASSETS SHAPE:", assets.shape)
        return pd.DataFrame(),pd.DataFrame()

    assets.columns = ['code','opening balances', 'outgoing balances']


    liabilities = pd.DataFrame(liab)
    if liabilities.shape[1] != 3:
        print("BAD LIAB SHAPE:", liabilities.shape)
        return pd.DataFrame(),pd.DataFrame()

    liabilities.columns = ['code', 'opening balances', 'outgoing balances']

    #write_to_csv(assets, date, liabilities)

    return assets,liabilities
def get_data_from_102(link,thread_local):
    if pd.isna(link):
        return None
    cb = 'https://www.cbr.ru'
    responce = thread_local.get((cb + link))
    soap = BeautifulSoup(responce.content, 'html.parser')

    x = soap.find('td', class_= 'bold')
    y = x.get_text(strip=True)
    while 'Финансовый результат после' not in y:
        x = x.find_next('td')
        y = x.get_text(strip=True)

    x = x.find_next('tr')
    x = x.find_next('tr')
    x = x.find_all('td')[-1]

    y = int(x.get_text(strip=True).replace('\xa0', ''))
    if y != 0:
        return y

    x = x.find_next('tr')
    x = x.find_all('td')[-1]
    y = int(x.get_text(strip=True).replace('\xa0', ''))*-1
    return y




def get_data_from_123(link,thread_local):
    cb = 'https://www.cbr.ru'
    responce = thread_local.get((cb + link))
    soap = BeautifulSoup(responce.content, 'html.parser')

    x = soap.find('td', class_ = 'right').get_text(strip=True).replace(' ', '')

    return int(x)


def get_data_from_135(link,thread_local):
    try:
        cb = 'https://www.cbr.ru'
        #aa = 'https://www.cbr.ru/banking_sector/credit/coinfo/f101?regnum=1481&dt=2025-01-01'
        responce = thread_local.get((cb + link))
        #responce = get(aa)
        soap = BeautifulSoup(responce.content, 'html.parser')
        h = []
        x = soap.find_all('tr')[1:4]
        for row in x:
            text = row.find('td', class_ = 'right').get_text(strip=True).replace(',', '.')
            h.append((text))
        return h
    except:
        return None



def month_data(assets, liabilities,date):

    Corporate_loans = list(map(str,range(442,459)))
    Corporate_loans.extend(['45.0','45.1'])
    Consumer_loans = ['45.2']

    Corporate_deposits = list(map(str,range(410,423)))
    Corporate_deposits.append('42.1')
    Consumer_deposits = ['42.2']

    loans_to_banks = ['32.1','32.2']
    money = ['20.0', '301', '302','319','324']
    #other_assets = ['459','463','47.1','474','475','478','506','507','509','526','60.0','604','608','609','610']
    #other_assets = ['459','463','47.1','474','475','478','506','507','509','526','60.0','604','609','610','620']
    other_assets = ['459','463','47.1','474','475','478','506','507','509','526','60.0','604','609','610']

    securities = ['501','502','504']


    def code_mapping():


        as_map = dict(zip(assets['code'], assets['outgoing balances']))
        liab_map = dict(zip(liabilities['code'], liabilities['outgoing balances']))

        corp_d = [liab_map[code] for code in Corporate_deposits if code in liab_map]
        corp_d = sum(list(map(int, corp_d)))

        cons_d = [liab_map[code] for code in Consumer_deposits if code in liab_map]
        cons_d = sum(list(map(int, cons_d)))


        corp_l = [as_map[code] for code in Corporate_loans if code in as_map]
        corp_l = sum(list(map(int,corp_l)))

        res_corp_l = [liab_map[code] for code in Corporate_loans if code in liab_map]
        res_corp_l = sum(list(map(int, res_corp_l)))

        cons_l = [as_map[code] for code in Consumer_loans if code in as_map]
        cons_l = sum(list(map(int, cons_l)))

        res_cons_l = [liab_map[code] for code in Consumer_loans if code in liab_map]
        res_cons_l = sum(list(map(int, res_cons_l)))

        bank_credit  = [as_map[code] for code in loans_to_banks if code in liab_map]
        bank_credit = sum(list(map(int, bank_credit)))
        res_bank_credit  = [liab_map[code] for code in loans_to_banks if code in liab_map]
        res_bank_credit = sum(list(map(int, res_bank_credit)))


        mon = [as_map[code] for code in money if code in as_map]
        mon = sum(list(map(int, mon)))
        res_mon = [liab_map[code] for code in money if code in liab_map]
        res_mon = sum(list(map(int, res_mon)))

        oa = [as_map[code] for code in other_assets if code in as_map]
        oa = sum(list(map(int, oa)))
        res_oa = [liab_map[code] for code in other_assets if code in liab_map]
        res_oa = sum(list(map(int, res_oa)))

        sec = [as_map[code] for code in securities if code in as_map]
        sec = sum(list(map(int, sec)))
        res_sec = [liab_map[code] for code in securities if code in liab_map]
        res_sec = sum(list(map(int, res_sec)))


        return corp_d, cons_d,corp_l - res_corp_l,cons_l - res_cons_l, bank_credit - res_bank_credit, mon, oa, sec - res_sec


    corp_d, cons_d,corp_l, cons_l, bank_l, mon, oa, sec = code_mapping()

    res = [cons_l,corp_l,cons_d,corp_d, bank_l,mon, oa,sec]
    return res



def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session

def result_data(url):

    array_links = parser(url)

    def process(row):
        try:
            assets, liabilities = get_data_from_101(row.date,row.f101,get_session())
            ass = month_data(assets, liabilities,row.date)
            ass.append(get_data_from_123(row.f123,get_session()))
            ass.extend(get_data_from_135(row.f135,get_session()))
            ass.append(get_data_from_102(row.f102,get_session()))
            return row.date, ass
        except Exception as e:
            print("FALIED ROW:", row.date, e)
            return row.date, [0]*12

    with ThreadPoolExecutor(max_workers = None) as executor:
        results = list(executor.map(process, array_links.itertuples()))

    res = {
        date: values for date, values in results}

    df = pd.DataFrame(res, index = ['Кредиты физ.лицам','Кредиты юр.лицам', 'Депозиты физ.лиц', 'Депозиты юр.лиц', 'Кредиты банкам','Денеж. средства и их ~','Прочие активы','ЦБ', 'Собственный капитал', 'H1.1', 'H1.2', 'H1.0','Прибыль'])

    return df, Bank_name



def broken_row():
    page_link = 'https://www.cbr.ru/banking_sector/credit/coinfo/f101?regnum=1481&dt=2026-01-01'
    responce = get(page_link, )
    soap = BeautifulSoup(responce.content, 'html.parser')

    res = {}
    b = soap.find_all('div', class_ = 'table-caption')[1]

    x = b.find_all('p')[1:]

    for item in x:
        index = item.find('nobr')
        if not index:
            continue
        s = index.text.split('—')[1].replace(' ','')
        index.extract()
        res[s] = (item.get_text(strip=True).replace(' ','').split(','))
    pas = {}

    df1 = pd.DataFrame.from_dict(res, orient = 'index')
    df = pd.DataFrame.from_dict(res, orient = 'index')
    df = df.reset_index().rename(columns = {'index' : 'code'})
    df['code'] = df['code'].astype('string')
    return df

def decoder(dat):
    data = dat[:]
    code = pd.read_csv('data/NAMES.csv')

    code.columns = ['plan', 'code','name', 'type']
    code['code'] = code['code'].astype('string')

    code_mapping = dict(zip(code['code'], code['name']))
    data.insert(1,'name', data['code'].map(code_mapping)) # где совпадений нет заменил на NULL

    elem = broken_row() # получили таблицу с составными ключами (20.0)
    for col in [0,1,2]: # для каждого столбца заменили кодировку на текст
        elem[col] = elem[col].map(code_mapping)

    elem['name'] = elem[[0,1,2]].fillna('').agg('\n'.join, axis = 1) # склеили столбцы заменяя NULL на '' используя разделитель
    elem = elem[['code','name']]

    elem_mapping = dict(zip(elem['code'], elem['name']))

    mask = data['name'].isna() # берем только те значения где в name пусто
    #data['name'] = data['name'].map(elem_mapping) было
    data.loc[mask,'name'] = data.loc[mask,'code'].map(elem_mapping) #  условие берем те name где пусто


    #data.to_csv('result.csv')
    #elem.to_csv('res.csv')'''
    return data
