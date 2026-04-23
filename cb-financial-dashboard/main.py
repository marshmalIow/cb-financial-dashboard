import calendar

import dash
import pandas
import numpy as np
import time
import traceback
from dash import dash_table

import pandas as pd
from dash import Dash, dcc, html, Input, Output

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from src.functions import *

def update_fig(fig,x):
    fig.update_xaxes(
        tickformat='%-d-%-m-%y',
        tickmode='array',
        tickvals=x[::2],
        tickangle=-50,
        showgrid=True,
        gridcolor='#f2f2f2',
        showline=True,
        linecolor='#f2f2f2',
        mirror=True,

    )
    fig.update_yaxes(

        #autorange = False,
        showgrid=True,
        gridcolor='#f2f2f2',
        tickmode='array',

    )
    fig.update_layout(
        plot_bgcolor='white',
        showlegend=False,

        margin=dict(l=60, r=15, t=80, b=60),
        bargap=0.3,

        barmode = 'stack',
        hovermode = 'x unified',
        hoverlabel = dict(
            font=dict(
                size=13,
                family='Verdana',
                color="black"
            ),
            namelength=-1,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.1)"
        ),
    )
    return fig

app = Dash(__name__)
def graph_assets_share(df):
    fig = go.Figure()
    credit = (df.loc['Кредиты физ.лицам'] + df.loc['Кредиты юр.лицам']) / 1_000_000
    other = (df.loc['Прочие активы'] + df.loc['Денеж. средства и их ~'] + df.loc['Кредиты банкам']) / 1_000_000
    all_active = (credit + other) + df.loc['ЦБ'] /1_000_000
    credit = credit / all_active
    other = other / all_active
    cb = df.loc['ЦБ'] / (1_000_000 * all_active)

    fig.add_trace(
        go.Scatter(
            x=df.columns,
            y=[0] * len(df.columns),
            mode="lines",
            name="Дата",
            line=dict(
                # color="rgba(0,0,0,0)",
                width=0
            ),
            customdata=[d.strftime('%d-%m-%Y') for d in df.columns],
            hovertemplate="<b>Дата: %{customdata}</b><extra></extra>",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Bar(
            x=df.columns,
            y = credit,
            #marker=dict(color='#8C4743'),
            name='net Кредитный портфель',
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.columns,
            y = other,
            name='Прочие активы',
            #marker=dict(color='#93AA00'),
        )
    )
    fig.add_trace(
        go.Bar(
            x=df.columns,
            y = cb,
            name='net ЦБ',
            #marker=dict(color='#803E75'),
            #marker=dict(color='#309DFF'),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.columns,
            y = all_active,
            name='Всего Активы : ',
            line=dict(color="rgba(0,0,0,0)"),
            hovertemplate=
            "<b>Итого: %{y:,.0f} млрд</b><extra></extra>",
            hoverlabel=dict(
                font=dict(
                    size=20,
                    family='Verdana',
                ),
                namelength=-1
            ),
            #marker=dict(color='#309DFF'),
        )
    )
    for x,v in zip(df.columns, all_active):
        t = f"{v/1000:.0f}" if all_active.max() >= 10000 else  f"{v:.0f}"
        fig.add_annotation(
            x = x,
            y = 1.01,
            text=t,
            showarrow=False,
            textangle=-40,
            xanchor = "center",
            yanchor="bottom",
            font = dict (
                size=10,
                family = 'Verdana',
            ),
        )

    fig = update_fig(fig,df.columns)


    fig.update_xaxes(
        range=[(df.columns.min() - pd.Timedelta(days=40)),
               df.columns.max() + pd.Timedelta(days=40)])
    fig.update_yaxes(

        tickformat = '.0%',
        range=[0, 1.1]
    )
    fig.update_layout(

        title='Активы',
        barmode = 'stack',
        hovermode = 'x unified',
        hoverlabel=dict(
            font=dict(
                size=12,
                family='Verdana',
                color = "black"
            ),
            namelength=-1,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor = "rgba(0,0,0,0.1)"
        ),
    )




    return fig

def graph_assets(df):

    fig = go.Figure()
    series = {
        'Денеж. средства и их ~': '#E9C46A',
        'Кредиты банкам' : '#2A9D8F',
        'Прочие активы': '#264653'
    }

    fig.add_trace(
        go.Scatter(
            x=df.columns,
            y=[0] * len(df.columns),
            mode="lines",
            name="Дата",
            line=dict(
                #color="rgba(0,0,0,0)",
                width=0
            ),
            customdata=[d.strftime('%d-%m-%Y') for d in df.columns],
            hovertemplate="<b>Дата: %{customdata}</b><extra></extra>",
            showlegend=False,
            hoverinfo="skip"
        )
    )
    credit = (df.loc['Кредиты физ.лицам'] + df.loc['Кредиты юр.лицам']) / 1_000_000
    fig.add_trace(
        go.Bar(

            x=df.columns,
            y=credit,
            name='net Кредитный портфель',
            marker=dict(color='#E76F51'),
            hovertemplate=
            "%{fullData.name}: " +
            "%{y:,.0f} млрд" +
            "<extra></extra>"

        )
    )
    fig.add_trace(
        go.Bar(

            x=df.columns,
            # y=df.loc[name] / 1_000_000,
            y=df.loc['ЦБ'] / 1_000_000,
            name='net ЦБ',
            marker=dict(color='#F4A261'),

            customdata=df.loc['ЦБ'] / 1_000_000,
            hovertemplate=
            "%{fullData.name}: " +
            "%{y:,.1f} млрд" +
            "<extra></extra>"

        )
    )
    for name, color in series.items():

        fig.add_trace(
            go.Bar(

                x=df.columns,
                #y=df.loc[name] / 1_000_000,
                y = df.loc[name] / 1_000_000,
                name = name,
                marker=dict(color=color),
                customdata = df.loc[name]/1_000_000,
                hovertemplate=
                "%{fullData.name} : " +
                "%{y:,.1f} млрд" +
                "<extra></extra>"

            )
        )


    fig.add_trace(
        go.Scatter(
            x=df.columns,
            y=(df.loc['Денеж. средства и их ~']+ df.loc['Кредиты банкам']+ df.loc['ЦБ']+df.loc['Прочие активы'])/1_000_000 + credit,
            mode="lines",
            name="Итого",
            line=dict(color="rgba(0,0,0,0)"),  # скрываем линию
            hovertemplate=
            "<b>Итого: %{y:,.0f} млрд</b><extra></extra>",
            hoverlabel = dict(
                font=dict
                    (
                    size=20,
                    family='Verdana',
                ),
                namelength=-1
            ),
        )
    )


    fig = update_fig(fig,df.columns)


    fig.update_xaxes(
        range=[(df.columns.min() - pd.Timedelta(days=40)),
               df.columns.max() + pd.Timedelta(days=40)])
    fig.update_yaxes(

        tickmode='array',
        range=[0, sum((df.loc['Прочие активы'].max(),df.loc['Денеж. средства и их ~'].max(),df.loc['ЦБ'].max(),df.loc['Кредиты банкам' ].max(),(df.loc['Кредиты физ.лицам']+ df.loc['Кредиты юр.лицам']).max())) / 1_000_000  ])
    fig.update_layout(

        title='Активы, млрд',
        barmode = 'stack',
        hovermode = 'x unified',
        hoverlabel=dict(
            font=dict(
                size=12,
                family='Verdana',
                color = "black"
            ),
            namelength=-1,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor = "rgba(0,0,0,0.1)"
        ),
    )

    return fig


def graph_capital(data):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data / 1_000_000,
            name = 'Капитал',
            marker=dict(color='#7366BD'),
            hovertemplate='%{y:,.0f} млрд'
        )
    )

    fig = update_fig(fig,data.index)
    fig.update_xaxes(
        range = [(data.index.min() - pd.Timedelta(days = 40)),
                 data.index.max() + pd.Timedelta(days = 40)])
    fig.update_yaxes(

        tickmode='array',
        range = [0, data.max()*1.3/1_000_000] )
    fig.update_layout(
        title = 'Капитал, млрд')

    return fig

def graph_profit_bar(data):
    df = pd.to_numeric(data, errors='coerce')

    df.iloc[0] = 0
    df.index = (df.index - pd.DateOffset(months = 1)).to_period('M').to_timestamp()
    df = df.interpolate(method = "time")
    df = df[1:]

    profit = df.groupby(df.index.year).diff()
    profit = profit.fillna(df)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=profit.index,
            y=profit / 1_000_000,
            name = 'Прибыль',
            marker=dict(color='#7366BD'),
            hovertemplate="%{y:.2f} млрд",

        )
    )

    fig = update_fig(fig,profit.index)

    fig.update_xaxes(

        range=[(profit.index.min() - pd.Timedelta(days=40)),
               profit.index.max() + pd.Timedelta(days=40)],
        tickvals = profit.index,
        ticktext = profit.index.strftime('%b %y'),
        tickfont = dict(
            size=10,
            family='Verdana',
        ),

    )

    fig.update_yaxes(

        range=[min(0,profit.min()* 1.3 / 1_000_000), profit.max() * 1.3 / 1_000_000])


    fig.update_layout(
        title = 'Прибыль, млрд',
        barmode='stack',
        hovermode='x unified',
    )
    return fig

def graph_ROE(df):

    data = df.loc[['Прибыль','Собственный капитал']]

    data.loc['Прибыль','2024-01-01'] = 0

    data.columns = pd.to_datetime(data.columns) - pd.DateOffset(months=1)
    data.loc['Прибыль'] = (pd.to_numeric(data.loc['Прибыль'], errors='coerce').interpolate(method = 'time'))

    data = data.iloc[:,1:]

    res = data.loc['Прибыль']
    profit = res.groupby(data.columns.year).diff()
    profit = profit.fillna(res)

    capital = data.loc['Собственный капитал']


    roe = profit.rolling(window=1).sum()*12/capital.rolling(window=1).mean()
    roe = roe.dropna()
    roe_ytd = data.loc['Прибыль'] / data.loc['Собственный капитал'].groupby(data.columns.year).expanding().mean().reset_index(level=0, drop=True)
    roe_annualized = roe_ytd*12/data.columns.month

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=roe.index,
            y=roe,
            name = "ROE month",
            mode='lines+markers',
            line=dict(shape='spline'),
            hovertemplate= '%{y:.2%}',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=roe.index,
            y=roe_annualized,
            name = "ROE YTD",
            mode='lines+markers',
            line=dict(shape='spline'),
            hovertemplate= '%{y:.2%}',
        )
    )
    y_min = min(roe.min(), roe_annualized.min())
    fig = update_fig(fig, data.columns)
    fig.update_yaxes(
        tickformat = '.0%',
        range = [y_min*1.2 if y_min < 0 else y_min*0.8, max(roe_annualized.max(),roe.max())*1.2]

    )
    fig.update_xaxes(
        tickvals=profit.index,
        ticktext=profit.index.strftime('%b %y'),
        tickfont=dict(
            size=10,
            family='Verdana',
        ),

    )
    fig.update_layout(
        title='ROE, %',

    )





    return fig

def graph_profit_scatter(data):
    df = pd.to_numeric(data, errors='coerce')

    df.iloc[0] = 0
    df.index = (df.index - pd.DateOffset(months = 1)).to_period('M').to_timestamp()
    df = df.interpolate()
    df = df[1:]

    df = df.to_frame("value")
    df.index = pd.to_datetime(df.index)

    df["year"] = df.index.year
    df["month"] = df.index.month
    pivot = df.pivot(
        index="month",
        columns="year",
        values="value"
    )


    fig = go.Figure()
    for year in pivot.columns:
        fig.add_trace(
            go.Scatter(
                x = pivot.index,
                y = pivot[year] / 1_000_000,
                mode = 'lines+markers',
                name = str(year),
                hovertemplate = "%{y:,.1f} млрд",
            )
        )
    fig = update_fig(fig,pivot.index)

    fig.update_xaxes(
        tickmode='array',
        tickvals = pivot.index,
        tickangle = 0,
        ticktext = [calendar.month_abbr[i] for i in pivot.index]

    )

    fig.update_yaxes(
        tickmode='array',

        range = [min(0,pivot.min().min()*1.3/1_000_000), pivot.max().max()*1.3/1_000_000] )

    fig.update_layout(
        title = 'Прибыль YTD, млрд',
        barmode='stack',
        hovermode='x unified',
    )

    return fig

def create_fig(data,title):

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data / 1_000_000,
        mode='lines + markers + text',
        #text = (data/1_000_000).map(lambda x: f'{x:,.0f}'),
        #textposition='top center',

        textfont=dict(
            size=10,
            family='Verdana',
        ),
        hovertemplate='Дата: %{x|%d-%m-%Y}<br>Значение: %{y:,.1f} млрд <extra></extra>',
        line=dict(shape='spline'),


    ))
    for x,v in zip(data.index[::2], data[::2] / 1_000_000):
        t = f"{v / 1000:.0f}" if data.max()/ 1_000_000 >= 10000 else f"{v:.0f}"
        fig.add_annotation(
            x = x,
            y = v*1.03,
            text=t,
            showarrow=False,
            xanchor = "center",
            yanchor="bottom",
            font = dict (
                size=10,
                family = 'Verdana',
            ),
        )
    fig = update_fig(fig,data.index)

    end = round(data.max() * 1.15/ 1_000_000)
    start = round(data.min() * 0.9/ 1_000_000,-1)
    step = (end - start)*1.0 / 4
    if step > 10:
        step = round(step,-1)
    else:
        if step > 1:
            step = round(step)

    ticks = [start + i*step for i in range(5)]
    fig.update_yaxes(
        range = [start, end],
        tickvals = ticks)

    # ------- layout ----------
    fig.update_layout(
        title = title)
    return fig

def graph_h(df):
    fig = go.Figure()
    h_11 = pd.to_numeric(df.loc['H1.1'], errors='coerce')

    fig.add_trace(
        go.Scatter(
            x=df.columns,
            y=h_11,
            mode="lines",
            name="Дата",
            line=dict(
                # color="rgba(0,0,0,0)",
                width=0
            ),
            customdata=[d.strftime('%d-%m-%Y') for d in df.columns],
            hovertemplate="<b>Дата: %{customdata}</b><extra></extra>",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
        x=df.columns,
        y=h_11,
        name = 'H1.1',
        mode='lines + markers + text',
        hovertemplate="%{y:.1f}%",
        line=dict(shape='spline'),
        )
    )
    h_12 = pd.to_numeric(df.loc['H1.2'], errors='coerce')
    fig.add_trace(
        go.Scatter(
        x=df.columns,
        y=h_12,
        name='H1.2',
        mode='lines + markers + text',
        hovertemplate="%{y:.1f}%",
        line=dict(shape='spline'),
        )
    )
    h_10 = pd.to_numeric(df.loc['H1.0'], errors='coerce')
    fig.add_trace(
        go.Scatter(
        x=df.columns,
        y=h_10,
        name='H1.0',
        mode='lines + markers + text',
        hovertemplate="%{y:.1f}%",
        line=dict(shape='spline'),
        )
    )
    fig = update_fig(fig,df.columns)
    fig.update_yaxes(
        ticksuffix = "%"

    )
    fig.update_layout(

        title = 'Нормативы достаточности',
        barmode='stack',
        hovermode='x unified',
        showlegend=True,
    )

    return fig

app.layout = html.Div([
    html.Div([
        html.H1([
            "Отчетность банка ",
            html.Span(id = "title"),
            html.Span(" по формам ЦБ(101,102,123,135)")
        ], className = 'h1'),
        dcc.Dropdown(
            id="bank",
            options=[
                {"label": "Сбер", "value": "sber"},
                {"label": "МТС", "value": "mts"},
                {"label": "БСПБ", "value": "bspb"},
                {"label": "ТБанк", "value": "tbank"},
                {"label": "Яндекс", "value": "yandex"},
                {"label": "ВТБ", "value": "vtb"},
                {"label": "Совкомбанк", "value": "svcb"},
                {"label": "Озон Банк", "value": "ozon"},
            ],
            value="sber",
            clearable=False,
            className = 'dropdown'
        ),
        #dcc.Graph(id = "graph")
    ], className = 'Head'),
    html.Div([
        dcc.Loading(dcc.Graph(id='graph_profit_bar'), className='card'),
        dcc.Loading(dcc.Graph(id='graph_profit_scatter'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_assets'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_capital'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_assets_share'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_ROE'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_h'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_credit'), className = 'card'),
    ], className='block'),

    html.Div([
        dcc.Loading(dcc.Graph(id='graph_loans_cons'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_loans_corp'), className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_dep_cons'),  className = 'card'),
        dcc.Loading(dcc.Graph(id='graph_dep_corp'), className = 'card')
    ], className='block'),

])


banks = {
    "sber": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1027700132195",
    "mts": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1027739053704",
    "bspb": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1027800000140",
    "tbank": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1027739642281",
    "yandex": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1077711000091",
    "vtb": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1027739609391",
    "svcb": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1144400000425",
    "ozon": "https://www.cbr.ru/finorg/foinfo/reports/?ogrn=1227700133792",




}
cache = {}

@app.callback(
    Output("title", "children"),
    Output("graph_profit_bar", "figure"),
    Output("graph_profit_scatter", "figure"),
    Output("graph_assets", "figure"),
    Output("graph_capital", "figure"),
    Output("graph_assets_share", "figure"),
    Output("graph_ROE", "figure"),
    Output("graph_h", "figure"),
    Output("graph_credit", "figure"),

    Output("graph_loans_cons", "figure"),
    Output("graph_loans_corp", "figure"),
    Output("graph_dep_cons", "figure"),
    Output("graph_dep_corp", "figure"),
    Input("bank", "value")
)

def update_all(bank):
    try:
        if bank in cache:
            df, Bank_name = cache[bank]
        else:
            df, Bank_name = result_data(banks[bank])
            cache[bank] = (df, Bank_name)


        return (
            Bank_name,
            graph_profit_bar(df.loc['Прибыль']),
            graph_profit_scatter(df.loc['Прибыль']),
            graph_assets(df),
            graph_capital(df.loc['Собственный капитал']),
            graph_assets_share(df),
            graph_ROE(df),
            graph_h(df),
            create_fig(df.loc['Кредиты физ.лицам']+df.loc['Кредиты юр.лицам'],'Кредитованый портфель net'),

            create_fig(df.loc['Кредиты физ.лицам'], 'Кредитование физ.лиц, млрд'),
            create_fig(df.loc['Кредиты юр.лицам'], 'Кредитование юр.лиц, млрд'),
            create_fig(df.loc['Депозиты физ.лиц'], 'Депозиты физ.лиц, млрд'),
            create_fig(df.loc['Депозиты юр.лиц'], 'Депозиты юр.лиц, млрд')
        )
    except Exception:
        print(traceback.format_exc())
        return ["Ошибка"] + [go.Figure()]*8




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #links = parser()

    #df, Bank_name = result_data(banks['sber'])
    start_time = time.time()
    app.run(debug = True)
    end_time = time.time()
    print(end_time - start_time)
    #get_data_from_links(111)
    #month_data(1,1,1)




