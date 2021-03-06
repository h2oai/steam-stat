# STEAM STATS
#
# App allows users to upload steam logs to get insights on daily use of 
# H2O products
#
# Author: Karthik Guruswamy, karthik.guruswamy@h2o.ai
#
# Last updated: Nov 22, 2021
#

import os
import datetime
import time
from h2o_wave import main, app, Q, ui, data

import pandas as pd
import numpy as np

import pandasql as psql
from pandasql import sqldf

import altair as alt
import re


@app('/')
async def serve(q: Q):

    if not q.client.initialized:
            initialize_app_for_new_client(q)

    if q.args.file_upload:
            await handle_uploaded_data(q)

    if q.args.drill_button:
            await drill_down_charts(q)

    if q.args.back_button:
            await render_first_page(q)
            
    if q.args.show_timeline:
            await set_timeline(q)

    await q.page.save()

async def handle_uploaded_data(q: Q):
    """Saves a file uploaded by a user from the UI"""
    if q.page['back_button']:
            del q.page['back_button']
            del q.page['daily_peak_sessions_users']
            del q.page['product_usage']
            del q.page['user_usage']
    
    data_path = q.client.data_path

    # Download new dataset to data directory
    q.client.working_file_path = await q.site.download(url=q.args.file_upload[0], path=data_path)
    q.client.timeline = 'All'

    # Update views to end user
    render_table_summary_info(q)
    time.sleep(1)  # show the Upload Success for 1 second before refreshing this view
    render_upload_view(q)

async def render_first_page(q:Q):
    del q.page['back_button']
    del q.page['daily_peak_sessions_users']
    del q.page['product_usage']
    del q.page['user_usage']
    render_table_summary_info(q)
    q.client.state = "render_first_page"
    
async def drill_down_charts(q:Q):
    """Deletes tables and summary cards and renders nice charts"""
    del q.page['table']
    del q.page['peak_usage']
    del q.page['summary_view']
    del q.page['drill_button']
    del q.page['timeline']

    back_button = [ui.button(name='back_button', label='<< Back', primary=True)]
    q.page['back_button'] = ui.form_card(box='1 8 2 1',items=back_button)
    q.client.state = "render_charts"
    render_charts(q)

async def set_timeline(q:Q):
    q.client.timeline = q.args.choice_group

    if (q.client.state == "render_charts"):
        await drill_down_charts(q)
    else:
        await render_first_page(q)

def initialize_app_for_new_client(q):
    """Setup this Wave application for each browser tab by creating a page layout and setting any needed variables"""

    q.page['header'] = ui.header_card(
            box='1 1 11 1',
            title='Customer Steam Stats',
            subtitle='Upload sessions.csv to understand Steam Usage',
    )

    render_upload_view(q)

    q.page['author'] = ui.markdown_card(
            box='1 7 2 1',
            title='Please send App feedback to:',
            content='karthik.guruswamy@h2o.ai',
    )


    # Create a place to hold datasets where you are running wave
    q.client.data_path = './data'
    if not os.path.exists(q.client.data_path):
            os.mkdir(q.client.data_path)

    q.client.initialized = True
    q.client.timeline = 'All'


def render_upload_view(q: Q):
    """Sets up the upload-dataset card"""
    q.page['upload'] = ui.form_card(
            box='1 2 2 5',
            items=[
                    ui.separator(label='Upload sessions.csv'),
                    ui.file_upload(name='file_upload', label='Upload Data', multiple=False, file_extensions=['csv']),
            ]
    )


def render_table_summary_info(q: Q):
    """Sets up the view a file as ui.table card"""

    if (q.page['back_button']):
            del q.page['back_button']
            del q.page['daily_peak_sessions_users']
            del q.page['product_usage']
            del q.page['user_usage']

    # Raw data view
    labelx = "Raw Dataset. Viewing Date Range : "+q.client.timeline
    items = [ui.separator(label=labelx)]
    items.append(ui.text_xl(os.path.basename(q.client.working_file_path)))
    items.append(make_ui_table(file_path=q.client.working_file_path,n_rows=10000, name='head_of_table', timeline=q.client.timeline))
    q.page['table'] = ui.form_card(box='3 2 9 6', items=items)

    # Peak Usage view
    peak_usage = [ui.separator(label='Peak Usage by Day')]
    peak_usage.append(make_ui_processed(file_path=q.client.working_file_path,name='peak_by_day_stats', timeline=q.client.timeline))
    q.page['peak_usage'] = ui.form_card(box='6 8 6 -1',items=peak_usage)

    # Summary view
    summary = [ui.separator(label='Summary')]
    summary.append(make_ui_summary(file_path=q.client.working_file_path,name='summary', timeline=q.client.timeline))
    q.page['summary_view'] = ui.form_card(box='3 8 3 -1',items=summary)

    # Setup the 'Drill Down' button
    drill_button = [ui.button(name='drill_button', label='Drill Down  >>', primary=True)]
    q.page['drill_button'] = ui.form_card(box='1 8 2 1',items=drill_button)

    # Setup the Timeline Choices

    clabel = 'Date Range -> '+q.client.timeline
    q.page['timeline'] = ui.form_card(box = '1 9 2 5', items=[
        ui.choice_group(name='choice_group',label=clabel,value=q.client.timeline,
                        required=True,
                        choices=[
                            ui.choice('All','All'),
                            ui.choice('First 30 days','First 30 days'),
                            ui.choice('Recent 30 days','Recent 30 days'),
                            ui.choice('Recent 60 days','Recent 60 days'),
                            ui.choice('Recent month','Recent month'),
                            ui.choice('Prev month','Prev month'),
                            ui.choice('Recent year','Recent year'),
                            ui.choice('Prev year','Prev year')
                        ]
                        ),
        ui.button(name='show_timeline',label='Set Date Range',primary=True),
    ])


def make_ui_table(file_path: str, n_rows: int, name: str, timeline: str):
    """Creates a ui.table object from a csv file"""

    df = pd.read_csv(file_path)
    df = filter_rows_by_timeline(df, timeline)

    n_rows = min(n_rows, df.shape[0])
    

    table = ui.table(
            name=name,
            columns=[ui.table_column(name=str(x), label=str(x), sortable=True) for x in df.columns.values],
            rows=[ui.table_row(name=str(i), cells=[str(df[col].values[i]) for col in df.columns.values])
                      for i in range(n_rows)],
            groupable=True,
    )
    return table

def make_ui_summary(file_path: str, name: str, timeline: str):

    sessions = pd.read_csv(file_path)
    sessions = filter_rows_by_timeline(sessions, timeline)

    #
    # no. of rows and cols
    #
    
    n_rows = sessions.shape[0]
    n_cols = sessions.shape[1]


    #
    # Hours
    #

    qq = "select sum(session_duration_sec)/3600 as hours from sessions"
    hd = psql.sqldf(qq,locals())
    hours = round(hd['hours'].values[0],2)
    
    #
    # Min and Max timestamps
    #
    qq = """
                    select min(datetime(session_launch_unix,'unixepoch')) as min_ts, 
                               max(datetime(session_end_unix,'unixepoch')) as max_ts 
                    from sessions
                    where session_state='finished'
            """

    min_max_ts = psql.sqldf(qq, locals())
    
    min_ts = min_max_ts['min_ts'].values[0]  
    max_ts = min_max_ts['max_ts'].values[0]

    min_ts = datetime.datetime.strptime(min_ts, '%Y-%m-%d %H:%M:%S').strftime("%c")
    max_ts = datetime.datetime.strptime(max_ts, '%Y-%m-%d %H:%M:%S').strftime("%c")
    
    # 
    # Aggregate stats on users and products
    #
    if 'username' in sessions.columns:
                    qq = """
                                    select count(distinct username) as unique_users, 
                                               count(distinct version) as unique_versions
                                    from sessions
                                    where session_state='finished'
                            """

                    agg_users_products = psql.sqldf(qq, locals())
                    users = agg_users_products['unique_users'].values[0]
                    versions = agg_users_products['unique_versions'].values[0]
    else:
            users = "N/A"
            versions= "N/A"

    # 
    # Load Peak usage file and do analytics
    #
    peak_usage = pd.read_csv("data/peak_usage.csv")

    qq = """
                    select max(unique_users) as max_daily_peak,
                               avg(unique_users) as avg_daily_peak,
                               max(peak_cpus) as max_daily_cpus,
                               avg(peak_cpus) as avg_daily_cpus,
                               max(peak_gpus) as max_daily_gpus,
                               avg(peak_gpus) as avg_daily_gpus,
                               sum(case when unique_users > 0 then 1 else 0 end) as total_days_used,
                               sum(case when unique_users = 0 then 1 else 0 end) as total_days_not_used
                            from peak_usage
            """
    agg_peak = psql.sqldf(qq,locals())
    max_daily_peak = agg_peak['max_daily_peak'].values[0]
    avg_daily_peak = round(agg_peak['avg_daily_peak'].values[0],2)
    max_daily_cpus = agg_peak['max_daily_cpus'].values[0]
    avg_daily_cpus = round(agg_peak['avg_daily_cpus'].values[0],2)
    max_daily_gpus = agg_peak['max_daily_gpus'].values[0]
    avg_daily_gpus = round(agg_peak['avg_daily_gpus'].values[0],2)
    total_days_used = agg_peak['total_days_used'].values[0]
    total_days_not_used = agg_peak['total_days_not_used'].values[0]

    #
    # Load the aggregates into a list
    #
    data = [
                    ['Log Starts',min_ts],
                    ['Log Ends',max_ts],
                    ['Total Hours of Use',hours],
                    ['Total Sessions', n_rows],
                    ['# of Unique Users',users],
                    ['# of Unique Product Versions',versions],
                    ['Max Daily Users',max_daily_peak],
                    ['Avg Daily Users',avg_daily_peak],
                    ['Max Daily CPUs',max_daily_cpus],
                    ['Avg Daily CPUs',avg_daily_cpus],
                    ['Max Daily GPUs',max_daily_gpus],
                    ['Avg Daily GPUs',avg_daily_gpus],
                    ['Total Days Used',total_days_used],
                    ['Total Days Not Used',total_days_not_used]
               ]

    #
    # Ready to render results 
    #
    df_render = pd.DataFrame(data, columns = ['KPI', 'Values'])

    table = ui.table(
            name=name,
            columns=[ui.table_column(name=str(x), label=str(x), sortable=True) for x in df_render.columns.values],
            rows=[ui.table_row(name=str(i), cells=[str(df_render[col].values[i]) for col in df_render.columns.values])
                      for i in range(14)],
            downloadable=True
    )
    return table


def make_ui_processed(file_path: str, name: str, timeline: str):

    sessions = pd.read_csv(file_path)

    sessions = filter_rows_by_timeline(sessions, timeline)

    #
    # Min and Max timestamps
    #
    qq = """
                    select min(datetime(session_launch_unix,'unixepoch')) as min_ts, 
                               max(datetime(session_end_unix,'unixepoch')) as max_ts 
                    from sessions
                    where session_state='finished'
            """

    min_max_ts = psql.sqldf(qq, locals())
    min_ts = min_max_ts['min_ts'].values[0]
    max_ts = min_max_ts['max_ts'].values[0]

    # 
    # Aggregate stats on users and products
    #
    if 'ownerN' in sessions.columns:
            qq = """
                            select count(distinct username) as unique_users, 
                                       count(distinct version) as unique_versions 
                            from sessions
                            where session_state='finished'
                    """

            agg_users_products = psql.sqldf(qq, locals())
            users = agg_users_products['unique_users'].values[0]
            versions = agg_users_products['unique_versions'].values[0]
    else:
            users = "N/A"
            versions = "N/A"
            
    #
    # Steps to get to peak users and other peak aggs
    #
    qq = """
                    select *, datetime(session_launch_unix,'unixepoch') as start_ts, 
                                      datetime(session_end_unix,'unixepoch') as end_ts 
                    from sessions
                    where session_state='finished'
            """
    v_basetable = psql.sqldf(qq,locals())

    qq = """
                    select date(min_ts) as minval,
                               date(max_ts) as maxval
                            from min_max_ts
            """
    min_max = psql.sqldf(qq,locals())

    rx = pd.date_range(start=min_max['minval'].values[0], end=min_max['maxval'].values[0], freq='D')
    range_values = pd.DataFrame(rx)
    range_values.columns = ['day_present']

    qq = """
                    select *
                            from
                            (select * from v_basetable) a
                                    inner join range_values b
                            on 
                                    (date(a.start_ts) <= date(b.day_present) 
                                    and
                                     date(a.end_ts) >= date(b.day_present))
            """
    base_table_expanded = psql.sqldf(qq,locals())

    qq = """
                    select date(a.day_present) as 'Day Present',
                            sum(case when b.start_ts is null then 0 else 1 end) as 'Peak Sessions',
                            sum(case when b.cpu_count is null then 0 else b.cpu_count end) as 'Peak CPUs',
                            sum(case when b.gpu_count is null then 0 else b.gpu_count end) as 'Peak GPUs',
                            count(distinct username) as 'Unique Users'
                    from 
                            range_values a 
                                    left join 
                            base_table_expanded b 
                                    on (date(a.day_present) = date(b.day_present))
                    group by 1
                    order by 1
            """
    peak_usage = psql.sqldf(qq,locals())
    peak_usage.to_csv("data/peak_usage.csv",header=['day_present','peak_sessions','peak_cpus','peak_gpus','unique_users'])

    #
    # Ready to render results 
    #
    df_render = pd.DataFrame(peak_usage, columns = ['Day Present','Peak Sessions','Peak CPUs','Peak GPUs','Unique Users'])
    n_rows = df_render.shape[0]


    table = ui.table(
            name=name,
            columns=[ui.table_column(name=str(x), label=str(x), sortable=True,  data_type= np.where(re.search(r'Peak|Users', x),
                                               'number', 'string').item()) for x in df_render.columns.values],
            rows=[ui.table_row(name=str(i), cells=[str(df_render[col].values[i]) for col in df_render.columns.values])
                      for i in range(n_rows)],
            downloadable=True
    )

    return table

def render_charts(q:Q):
    sessions = pd.read_csv(q.client.working_file_path)
    sessions = filter_rows_by_timeline(sessions, q.client.timeline)

    peak_usage = pd.read_csv('data/peak_usage.csv')
    #header=['day_present','peak_sessions','peak_cus','unique_users'])               )
    
    spec = altair_area_line_chart(data=peak_usage,
                                x="day_present:T",
                                x_title="Day",
                                y1="peak_sessions:Q",
                                y1_title="Peak Sessions",
                                y1_color="brown",
                                y2="unique_users:Q",
                                y2_title="Unique Users",
                                y2_color="blue")
    
    
    q.page['daily_peak_sessions_users'] = ui.vega_card(
                                                    box='3 2 9 6',
                                                    title='Daily Peak Sessions and Unique Users',
                                                    specification=spec,
                                              )
    
    qq = """
           select version as product,count(*) as sessions
           from sessions
            group by 1
            order by 2 desc
        """

    product_usage = psql.sqldf(qq,locals())

    q.page['product_usage'] = ui.plot_card(
                        box='3 8 3 -1',
                        title='Version Usage by Sessions',
                        data=data(
                            fields=product_usage.columns.tolist(),
                            rows=product_usage.values.tolist(),
                            pack=True,
                            ),
                        plot=ui.plot(marks=
                            [ui.mark(
                                type='interval',
                                x='=sessions', x_title='Sessions',
                                y='=product', y_title='Version',
                                color='=sessions', x_min=0,
                                ),
                            ])
                    )


    qq = """
            select username, count(*) as sessions, round(sum(session_duration_sec)/3600,0) as hours
                from sessions
            group by 1
            order by 2 desc
            limit 15
        """

    user_usage = psql.sqldf(qq, locals())

    spec = altair_area_line_chart(data=user_usage,
                                x="username:O",
                                x_title="User",
                                y1="sessions:Q",
                                y1_title="Sessions",
                                y1_color="blue",
                                y2="hours:Q",
                                y2_title="Hours",
                                y2_color="orange")

    
    q.page['user_usage'] = ui.vega_card(
                                box='6 8 6 -1',
                                title='Top 15 Power Users by Sessions/Hours',
                                specification=spec,
                            )
    
def altair_bar_line_chart(data: pd, x: str, x_title: str, y1:str, y1_title:str, y1_color:str, y2:str, y2_title: str,y2_color: str):
    
    base = alt.Chart(data,title = "").encode(
            alt.X(x, title=x_title),
            tooltip=[x,y1,y2]
    )

    bar_A = base.mark_bar(color=y1_color).encode(
            alt.Y(y1, title=y1_title, axis=alt.Axis(titleColor=y1_color,labelColor=y1_color))

    )

    line_B = base.mark_line(color=y2_color).encode(
            alt.Y(y2, title=y2_title, axis=alt.Axis(titleColor=y2_color,labelColor=y2_color))
    )

    spec = alt.layer(bar_A, line_B).resolve_scale(y='independent').to_json()
    return spec   

def altair_area_line_chart(data: pd, x: str, x_title: str, y1:str, y1_title:str, y1_color:str, y2:str, y2_title: str,y2_color: str):
    
    base = alt.Chart(data,title = "").encode(
            alt.X(x, title=x_title),
            tooltip=[x,y1,y2]
    ).properties(width='container', height='container')

    area_A = base.mark_area(color=y1_color).encode(
            alt.Y(y1, title=y1_title, axis=alt.Axis(titleColor=y1_color,labelColor=y1_color))

    )

    line_B = base.mark_line(color=y2_color).encode(
            alt.Y(y2, title=y2_title, axis=alt.Axis(titleColor=y2_color,labelColor=y2_color))
    )

    spec = alt.layer(area_A, line_B).resolve_scale(y='independent').to_json()
    return spec   
     
def filter_rows_by_timeline(df: pd, x_filter: str):
 
#     ui.choice('All','All'),
#     ui.choice('First 30 days','First 30 days'),
#     ui.choice('Recent 30 days','Recent 30 days'),
#     ui.choice('Recent 60 days','Recent 60 days'),
#     ui.choice('Recent month','Recent month'),
#     ui.choice('Prev month','Prev month'),
#     ui.choice('Recent year','Recent year'),
#     ui.choice('Prev year','Prev year')
 

   # Create markers for filtering
   qq = """ select 
             max(date(session_launch_date)) as latest_day, 
              min(date(session_launch_date,'+30 days')) as first_30_days,
              max(date(session_launch_date, 'start of year')) as latest_year_start,
              max(date(session_launch_date, 'start of year','-1 year')) as prev_year_start,
                            
              max(date(session_launch_date, 'start of month')) as latest_month_start,
              max(date(session_launch_date, 'start of month','-1 month')) as prev_month_start,
              
              max(strftime('%Y', session_launch_date)) as current_year,
              max(strftime('%W', session_launch_date)) as current_week,
              max(date(session_launch_date,'-30 days')) as recent_30_days,
              max(date(session_launch_date,'-60 days')) as recent_60_days

         from df
      """

   markers = psql.sqldf(qq,locals()) 

   # Fallback
   df2 = df

   if (x_filter == 'First 30 days'):
       # First 30 days
       qq = "select a.* from df a join markers b where a.session_launch_date <=  first_30_days"
       df2 = psql.sqldf(qq,locals())

   if (x_filter == 'Recent 30 days'):
       # Recent 30 days
       qq = "select a.* from df a join markers b where a.session_launch_date >=  recent_30_days"
       df2 = psql.sqldf(qq,locals())

   if (x_filter == 'Recent 60 days'):
       # Recent 60 days
       qq = "select a.* from df a join markers b where a.session_launch_date >=  recent_60_days"
       df2 = psql.sqldf(qq,locals())

   if (x_filter == 'Recent month'):
       # Recent month
       qq = "select a.* from df a join markers b where a.session_launch_date >= latest_month_start"
       df2 = psql.sqldf(qq,locals())

   if (x_filter == 'Prev month'):
       # Prev month
       qq = "select a.* from df a join markers b where a.session_launch_date >= b.prev_month_start and a.session_launch_date < b.latest_month_start"
       df2 = psql.sqldf(qq,locals())

   if (x_filter == 'Recent year'):
       # Recent year
       qq = "select a.* from df a join markers b where a.session_launch_date >= b.latest_year_start"
       df2 = psql.sqldf(qq,locals())

   if (x_filter == 'Prev year'):
       # Prev year
       qq = "select a.* from df a join markers b where a.session_launch_date >= b.prev_year_start and a.session_launch_date < b.latest_year_start"
       df2 = psql.sqldf(qq,locals())

   return df2

