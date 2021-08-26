import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output
import dash_table
from plotly.subplots import make_subplots
import numpy as np
import dash_daq as daq
import datetime


# import data
data = pd.read_csv('summary_H2S.csv')
# fantest = pd.read_csv(r'.\fantest\fantest.csv')git add .

data['Time Stamp'] = pd.to_datetime(data['Time Stamp'])
# fantest['Time Stamp'] = pd.to_datetime(fantest['Time Stamp'])
Time_list = data['Time Stamp'].dt.date.unique().tolist()
Time_list.append(max(Time_list)+ datetime.timedelta(days=1))

# Define Time Marks for range slider
time_marks = {x:y for (x,y) in enumerate(Time_list)}
time_marks_checklist = {x:y.strftime('%m-%d') for (x,y) in enumerate(Time_list)}
# time_marks = {x:y for (x,y) in enumerate(data['Time Stamp'].sort_values().strftime('%m-%d').unique())}



# define colors
colors = ['rgb(31, 119, 180)',
          'rgb(255, 127, 14)',
          'rgb(44, 160, 44)',
          'rgb(214, 39, 40)',
          'rgb(188, 189, 34)',
          'rgb(148, 103, 189)',
          'rgb(140, 86, 75)',
          'rgb(227, 119, 194)',
          'rgb(127, 127, 127)',
          'rgb(23, 190, 207)',
          'rgb(67,67,67)',
          'rgb(115,115,115)',
          'rgb(49,130,189)',
          'rgb(189,189,189)' ]
color_discrete_maps = dict(zip(data['Site_ID'].unique(), colors))



#----------------------------------------------------------------------
app = dash.Dash(__name__)

# ------------------------------------------------------------------------------------------------------------
app.layout = html.Div([
    html.Div([html.H1(children="H2S Data Analysis and Visualization Webapp"),
              html.P(),
              html.P(),]),

    # Range slider
    html.Div([
        html.Label(['Choose the Date:'],style = {'font-weight':"bold"}),
        dcc.RangeSlider(
            id = 'range-slider',
            marks= time_marks_checklist,
            step=1,  # number of steps between values
            min=0,
            max=len(data['Time Stamp'].dt.date.unique()),
            value=[0, len(data['Time Stamp'].dt.date.unique())],  # default value initially chosen
            dots=True,  # True, False - insert dots, only when step>1
            allowCross=False,  # True,False - Manage handle crossover
            disabled=False,  # True,False - disable handle
            pushable=1,  # any number, or True with multiple handles
            updatemode='mouseup',  # 'mouseup', 'drag' - update value method
            included=True,  # True, False - highlight handle
            vertical=False,  # True, False - vertical, horizontal slider
            verticalHeight=900,  # hight of slider (pixels) when vertical=True
            className='None',
            # tooltip={'always visible': False,  # show current slider values
            #          'placement': 'bottom'},

        ),

    ]),

    html.Div([
        html.P(),
        html.P(),
        # Dash Table
        html.Label(['Summary Table:'],
                   style = {'font-weight':"bold"}),
        dash_table.DataTable(
            id='datatable_id',
            # data='data',
            # columns='columns',
            sort_action='native',
            sort_mode='multi',
            style_cell={'minWidth': 95, 'maxWidth': 95, 'Width': 95},
            style_data={
                'whiteSpace': "normal",
                'height': "auto"
            }
        ),
        html.P(),
        html.P(),
        html.P(),
        html.P(),
    ]),
    html.Div([
        html.P(),
        html.P(),
        html.P(),
        html.P(),
    ]),

    html.Div([html.Label(['H2S Concentration Plot:'],style = {'font-weight':"bold"}),]),


    html.Div([
        dcc.Checklist(
            id = 'checklist',
            options = [
                {'label':x, 'value':x, 'disable': False}
                for x in data['Site_ID'].unique()],
            value = data[data['Site_ID'].str.contains('PPB') == False]['Site_ID'].unique()
        )
    ]),

    html.Div([
        daq.BooleanSwitch(
            on=True,
            id='my-boolean-switch',
            label="Show Fan Test Label",
            labelPosition="top"
        )
    ]),


    html.Div([
        dcc.Graph(
            id='the_graph'
            ),

    ]),
])

# #------------------------------------------------------------------------
@app.callback(
    [Output('the_graph','figure'),
     Output('datatable_id','data'),
     Output('datatable_id','columns'),
],
    [Input('checklist','value'),
     Input('range-slider','value'),
     dash.dependencies.Input('my-boolean-switch', 'on')]
)
#
def update_graph(option_chosen,time_chosen,on):
    # ----------------------------------------------------------
# Define data based on the checklist

    time_range = [np.datetime64(time_marks[x]) for x in time_chosen]
    data_sl = data[data['Site_ID'].isin(option_chosen)]
    data_sl = data_sl[(data_sl['Time Stamp']>=time_range[0])&(data_sl['Time Stamp']<=time_range[1])]
    data_ppb = data_sl[data_sl['Site_ID'].str.contains('PPB')].copy()
    data_ppb.rename(columns={'H2S (PPM)': 'H2S (PPB)'}, inplace=True)
    data_ppb['H2S (PPB)'] = data_ppb['H2S (PPB)'] * 1000
    data_ppm = data_sl[data_sl['Site_ID'].str.contains('PPB') == False].copy()

# Define data to the table
    Max = data_sl.groupby('Site_ID', as_index=False)[['H2S (PPM)']].max().set_index('Site_ID')
    Min = data_sl.groupby('Site_ID', as_index=False)[['H2S (PPM)']].min().set_index('Site_ID')
    Avg = data_sl.groupby('Site_ID', as_index=False)[['H2S (PPM)']].mean().round(1).set_index('Site_ID')
    Max.columns = ['H2S, Max']
    Min.columns = ['H2S, Min']
    Avg.columns = ['H2S, Mean']
    data_stats = pd.concat([Max, Min, Avg], axis=1).reset_index()
    data_stats_totable = data_stats.to_dict('records')
    columns = [{'name': i, 'id': i, 'deletable': False, 'selectable': False} for i in data_stats.columns]



    if data_ppb.empty == False:
        subfig = make_subplots(specs=[[{"secondary_y": True}]])

        fig1 = px.line(data_ppm, x='Time Stamp', y='H2S (PPM)', color='Site_ID', color_discrete_map=color_discrete_maps,
                       height=800, width=1700, labels={'Time Stamp': 'Datetime'})
        fig2 = px.line(data_ppb, x='Time Stamp', y='H2S (PPB)', color='Site_ID',color_discrete_map=color_discrete_maps,
                       height=800, width=1700, labels={'Time Stamp': 'Datetime'})
        fig2.update_traces(yaxis="y2")
        subfig.add_traces(fig1.data + fig2.data)
        subfig.layout.yaxis2.title = "H2S (PPB)"

    else:
        fig1 = px.line(data_ppm, x='Time Stamp', y='H2S (PPM)', color='Site_ID',
                       height=800, width=1700, labels={'Time Stamp': 'Datetime'}, color_discrete_map=color_discrete_maps)
        subfig=fig1

    subfig.update_layout(width=1700, height=800)
    subfig.layout.xaxis.title = "Date Time"
    subfig.layout.yaxis.title = "H2S (PPM)"

    subfig.update_xaxes(title_font=dict(size=24),
                        tickfont=dict(size=16), ticks='inside', tickwidth=2, ticklen=6, showline=True,
                        linewidth=1.5, linecolor='black')

    subfig.update_yaxes(title_font=dict(size=24),
                        tickfont=dict(size=16), ticks='outside', tickwidth=2, ticklen=6, showline=True,
                        linewidth=1.5, linecolor='black', showgrid=True, gridcolor='lightgray', gridwidth=0.5)

    subfig.update_layout(
        {
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    subfig.update_layout(legend=dict(
        # orientation="h",
        # yanchor="bottom",
        # y=1.02,
        # xanchor="center",
        # x=1.02,
        font=dict(
            family="Courier",
            size=28,
            color="black"
        ),
        itemsizing='constant'),
        legend_title = '',
        # legend_title=dict(font_size=24)
    )

# Switch to turn/off the fantest
#     if on == True:
#         j=0 # parameter introduced to define colors
#         for i in fantest['Notion'].unique():
#             j+=1
#             fantestsub_df = fantest.groupby(['Notion']).get_group(i).reset_index()
#             for n in range(len(fantestsub_df)):
#                 subfig.add_vline(x=fantestsub_df['Time Stamp'][n],
#                                  line_dash="dash",
#                                  line_color = colors[j],
#                                  )
#                 subfig.add_annotation(
#                     x=fantestsub_df['Time Stamp'][n],
#                     y=1.06,
#                     yref='paper',
#                     showarrow=False,
#                     text=i,
#                 font=dict(size=16,color="black"))

    return subfig, data_stats_totable,columns




if __name__ == '__main__':
    app.run_server(port=4050)

