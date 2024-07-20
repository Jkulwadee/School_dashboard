import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# อ่านข้อมูลนักเรียน
student_data = pd.read_csv('student.csv')

# อ่านข้อมูลพิกัดละติจูดและลองติจูด
map_data = pd.read_csv('map.csv')

# รวมข้อมูล โดยใช้ schools_province แทน province
merged_data = pd.merge(student_data, map_data, left_on='schools_province', right_on='province')

# สร้างแผนที่
map_fig = px.scatter_mapbox(
    merged_data,
    lat="latitude",
    lon="longitude",
    hover_name="schools_province",
    hover_data={"totalstd": True, "totalmale": True, "totalfemale": True},
    size="totalstd",
    color="totalstd",
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=30,  # ขนาดสูงสุดของจุด
    zoom=5,       # ซูมให้แสดงประเทศไทย
    mapbox_style="carto-positron"
)

# ฟังก์ชันเพื่อสร้างกราฟวงกลม
def create_pie_chart(male_count, female_count):
    pie_data = pd.DataFrame({
        "Category": ["ชาย", "หญิง"],
        "Count": [male_count, female_count],
        "Color": ["#1f77b4", "#ff7f0e"]  # สีสำหรับชายและหญิง
    })

    pie_fig = px.pie(
        pie_data,
        names='Category',
        values='Count',
        color='Category',
        color_discrete_map={
            "ชาย": "#1f77b4",
            "หญิง": "#ff7f0e"
        },
        labels={"Category": "ประเภท", "Count": "จำนวน"},
        title="การแจกแจงชายและหญิง"
    )
    pie_fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    return pie_fig

# สร้าง Dropdown สำหรับเลือกจังหวัด
province_options = [{'label': province, 'value': province} for province in merged_data['schools_province'].unique()]

# สร้างกราฟบาร์เริ่มต้น (กราฟเปล่า)
bar_fig = px.bar(
    pd.DataFrame(columns=["Category", "Count"]),  # ข้อมูลเปล่า
    x="Category",
    y="Count",
    labels={"Category": "ประเภท", "Count": "จำนวน"},
    title="กราฟบาร์"
)

# สร้างแอป Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Dashboard การศึกษา: การแสดงผลข้อมูลนักเรียน",
        style={
            'textAlign': 'center',
            'color': '#ffffff',
            'font-family': 'Arial, sans-serif',
            'padding': '20px',
            'backgroundColor': '#003366'
        }
    ),

    html.H2(
        "แผนที่แสดงจำนวนและข้อมูลนักเรียนในแต่ละจังหวัด",
        style={
            'textAlign': 'center',
            'color': '#ffffff',
            'font-family': 'Arial, sans-serif',
            'padding': '10px',
            'backgroundColor': '#004080'
        }
    ),
    
    dcc.Graph(
        id='map',
        figure=map_fig,
        style={'height': '50vh', 'width': '100%'}
    ),
    
    html.Div([
        html.Label(
            "เลือกจังหวัด:",
            style={'font-family': 'Arial, sans-serif', 'font-size': '18px', 'padding': '10px', 'color': '#ffffff'}
        ),
        dcc.Dropdown(
            id='province-dropdown',
            options=province_options,
            value=merged_data['schools_province'].iloc[0],
            style={'font-family': 'Arial, sans-serif', 'width': '50%', 'margin': 'auto', 'color': '#003366'}
        )
    ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#004080'}),
    
    html.Div([
        html.Div([
            dcc.Graph(
                id='bar',
                figure=bar_fig,
                style={'height': '45vh', 'width': '100%'}
            )
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(
                id='pie-chart',
                figure=create_pie_chart(0, 0),
                style={'height': '45vh', 'width': '100%'}
            )
        ], style={'width': '50%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'padding': '20px'}),
], style={'backgroundColor': '#001f3f'})

# Callback function เพื่ออัปเดตกราฟบาร์และกราฟวงกลมตามการเลือกจาก Dropdown
@app.callback(
    [Output('bar', 'figure'),
     Output('pie-chart', 'figure')],
    Input('province-dropdown', 'value')
)
def update_charts(selected_province):
    if selected_province is None:
        return bar_fig, create_pie_chart(0, 0)
    
    # กรองข้อมูลตามจังหวัดที่เลือก
    filtered_data = merged_data[merged_data['schools_province'] == selected_province]
    
    # เปลี่ยนข้อมูลเป็นรูปแบบที่เหมาะสมสำหรับกราฟบาร์
    bar_data = pd.DataFrame({
        "Category": ["ชาย", "หญิง", "รวม"],
        "Count": [filtered_data['totalmale'].sum(), filtered_data['totalfemale'].sum(), filtered_data['totalstd'].sum()],
        "Color": ["#1f77b4", "#ff7f0e", "#2ca02c"]
    })
    
    # สร้างกราฟบาร์ใหม่
    new_bar_fig = px.bar(
        bar_data,
        x="Category",
        y="Count",
        color="Category",
        color_discrete_map={
            "ชาย": "#1f77b4",
            "หญิง": "#ff7f0e",
            "รวม": "#2ca02c"
        },
        labels={"Category": "ประเภท", "Count": "จำนวน"},
        title=f"จำนวนชาย, หญิง และรวมในจังหวัด {selected_province}"
    )
    
    new_bar_fig.update_traces(marker=dict(line=dict(width=2, color='black')))
    new_bar_fig.update_layout(xaxis_title='ประเภท', yaxis_title='จำนวน', xaxis_tickangle=-45)
    
    male_count = filtered_data['totalmale'].sum()
    female_count = filtered_data['totalfemale'].sum()
    
    pie_fig = create_pie_chart(male_count, female_count)
    
    return new_bar_fig, pie_fig

if __name__ == '__main__':
    app.run_server(debug=True)
