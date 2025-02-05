import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.io as pio

# Load the dataset
df = pd.read_csv('Loan_data.csv')

# Clean the data
df['Gender'] = df['Gender'].fillna(df['Gender'].mode()[0])
df['Dependents'] = df['Dependents'].fillna(df['Dependents'].mode()[0])
df['Self_Employed'] = df['Self_Employed'].fillna(df['Self_Employed'].mode()[0])
df['LoanAmount'] = df['LoanAmount'].fillna(df['LoanAmount'].median())
df['Loan_Amount_Term'] = df['Loan_Amount_Term'].fillna(df['Loan_Amount_Term'].median())
df['Credit_History'] = df['Credit_History'].fillna(df['Credit_History'].mode()[0])

# Initialize the Dash app
app = dash.Dash(__name__)
server=app.server

# App layout
app.layout = html.Div([
    html.H1('Loan Approval Dashboard', className='header', style={'textAlign': 'center', 'color': 'white'}),
    
    html.Div([
        html.Label('Filter by Property Area:', style={'color': 'white'}),
        dcc.Dropdown(
            id='property_area_filter',
            options=[{'label': area, 'value': area} for area in df['Property_Area'].unique()],
            value=df['Property_Area'].unique().tolist(),
            multi=True,
            style={'backgroundColor': 'black', 'color': 'white'}, 
            className='custom-dropdown' 
        )
    ], style={'width': '40%', 'margin': 'auto'}),
    
    # First row: Pie chart and Histogram
    html.Div([
        html.Div([
            dcc.Graph(id='loan_approval_pie'),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='loan_amount_distribution'),
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ]),
    
    # Second row: Donut chart and Heatmap
    html.Div([
        html.Div([
            dcc.Graph(id='loan_status_donut'),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='loan_approval_by_gender'),
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ]),
    
    # Dependents slider (moved above the donut chart)
    html.Div([
        html.Label('Filter by Number of Dependents:', style={'color': 'white'}),
        dcc.Slider(
            id='dependents_slider',
            min=0,
            max=3,
            step=None,
            marks={
                0: '0',
                1: '1',
                2: '2',
                3: '3+'
            },
            value=0  
        )
    ], style={'width': '40%', 'margin': 'auto', 'padding': '20px 0'}),
    
    # Third row: Scatter plot (full width)
    html.Div([
        dcc.Graph(id='income_vs_loan_amount'),
    ]),
], style={'backgroundColor': 'black', 'color': 'white'})

# Callbacks for interactivity
@app.callback(
    Output('loan_approval_pie', 'figure'),
    Input('property_area_filter', 'value')
)
def update_pie_chart(selected_areas):
    filtered_df = df[df['Property_Area'].isin(selected_areas)]
    pie_chart = px.pie(filtered_df, names='Loan_Status', title='Loan Approval Distribution',
                       color_discrete_sequence=px.colors.sequential.Plasma)
    pie_chart.update_layout(
        paper_bgcolor='black', 
        plot_bgcolor='black', 
        font_color='white',
        title_font_color='white'
    )
    # Save the pie chart as HTML
    pio.write_html(pie_chart, 'loan_approval_pie.html')
    return pie_chart

@app.callback(
    Output('loan_approval_by_gender', 'figure'),
    Input('property_area_filter', 'value')
)
def update_heatmap(selected_areas):
    # Filter the data based on selected property areas
    filtered_df = df[df['Property_Area'].isin(selected_areas)]
    
    # Create a heatmap using px.density_heatmap
    heatmap = px.density_heatmap(
        filtered_df,
        x='Gender',
        y='Loan_Status',
        title='Loan Approval Heatmap by Gender',
        color_continuous_scale='Blues',
        text_auto=True  # Automatically add text annotations
    )
    
    # Update layout for dark theme
    heatmap.update_layout(
        paper_bgcolor='black', 
        plot_bgcolor='black', 
        font_color='white',
        title_font_color='white',
        xaxis_title='Gender',
        yaxis_title='Loan Status'
    )
    
    # Save the heatmap as HTML
    pio.write_html(heatmap, 'loan_approval_by_gender_heatmap.html')
    
    return heatmap

@app.callback(
    Output('income_vs_loan_amount', 'figure'),
    Input('property_area_filter', 'value')
)
def update_scatter_plot(selected_areas):
    filtered_df = df[df['Property_Area'].isin(selected_areas)]
    scatter_plot = px.scatter(filtered_df, x='ApplicantIncome', y='LoanAmount', color='Loan_Status', title='Applicant Income vs Loan Amount',
                              size='ApplicantIncome', color_discrete_sequence=px.colors.sequential.Plasma)
    scatter_plot.update_layout(
        paper_bgcolor='black', 
        plot_bgcolor='black', 
        font_color='white',
        title_font_color='white'
    )
    # Save the scatter plot as HTML
    pio.write_html(scatter_plot, 'income_vs_loan_amount.html')
    return scatter_plot

@app.callback(
    Output('loan_amount_distribution', 'figure'),
    Input('property_area_filter', 'value')
)
def update_histogram(selected_areas):
    filtered_df = df[df['Property_Area'].isin(selected_areas)]
    histogram = px.histogram(filtered_df, x='LoanAmount', nbins=30, title='Loan Amount Distribution',
                             color_discrete_sequence=px.colors.sequential.Plasma)
    histogram.update_layout(
        paper_bgcolor='black', 
        plot_bgcolor='black', 
        font_color='white',
        title_font_color='white'
    )
    # Save the histogram as HTML
    pio.write_html(histogram, 'loan_amount_distribution.html')
    return histogram

@app.callback(
    Output('loan_status_donut', 'figure'),
    Input('property_area_filter', 'value'),
    Input('dependents_slider', 'value')
)
def update_donut_chart(selected_areas, selected_dependents):
    # Filter by Property Area
    filtered_df = df[df['Property_Area'].isin(selected_areas)]
    
    # Filter by Dependents
    if selected_dependents == 3:
        filtered_df = filtered_df[filtered_df['Dependents'] == '3+']
    else:
        filtered_df = filtered_df[filtered_df['Dependents'] == str(selected_dependents)]
    
    # Create donut chart
    donut_chart = px.pie(
        filtered_df, 
        names='Loan_Status', 
        title=f'Loan Status Distribution for Dependents = {selected_dependents}',
        hole=0.4,  # Creates a donut chart
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    donut_chart.update_layout(
        paper_bgcolor='black', 
        plot_bgcolor='black', 
        font_color='white',
        title_font_color='white'
    )
    # Save the donut chart as HTML
    pio.write_html(donut_chart, 'loan_status_donut.html')
    return donut_chart

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
