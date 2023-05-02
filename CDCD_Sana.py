import streamlit as st
import requests
import pandas as pd
import altair as alt


# Task 1 Getting data from Spreadsheet using API Key
api_key = 'AIzaSyD_D9avHS5Xz5bcYlpzf17CKdqViBqkVlY'
spreadsheet_id = '1lI86lSA4StHdeSfmsCjpBr-6maS37oOy34MfSiQZUIs'
sheet_name = 'Sheet1'

url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}?key={api_key}'

response = requests.get(url)

googlesheetdata = response.json()['values']
df = pd.DataFrame(googlesheetdata[1:], columns=googlesheetdata[0])


#Task 2 Setting dashboard header

st.set_page_config(layout='wide')
st.header("Consumer Financial Complaints Dashboard")
st.markdown("""
<style>
body {
    background-color: #e6f2ff;
}
</style>
""", unsafe_allow_html=True)


#Task 3 Setting states filer and based on the filter getting KPI
states = df['state'].unique().tolist()
with st.container():
    st.subheader("All States")
    state = st.selectbox('Select a state', ['All'] + states)
    if state != 'All':
        filtered_df = df[df['state'] == state]
    else:
        filtered_df = df
    

    # Define the functions to calculate the KPIs
    def total_complaints(df):
        return len(df)

    def closed_complaints(df):
        return len(df[df['company_response'] == 'Closed with explanation'])

    def timely_responses(df):
        if len(df) == 0:
            return 0
        else:
            return round(len(df[df['timely'] == 'Yes']) / len(df) * 100, 2)

    def in_progress_complaints(df):
        return len(df[df['company_response'] == 'In progress'])

    total_complaints = total_complaints(filtered_df)
    closed_complaints = closed_complaints(filtered_df)
    timely_responses = timely_responses(filtered_df)
    in_progress_complaints = in_progress_complaints(filtered_df)

    col1, col2, col3, col4 = st.columns((1, 1, 1, 1))
    # Display the transformed data in the columns
    col1.metric("Total Complaints", f"{total_complaints}")
    col2.metric("Closed Complaints", f"{closed_complaints}")
    col3.metric("% Timely Response", f"{timely_responses}")
    col4.metric("In Progress Complaints", f"{in_progress_complaints}")

#Task 4 Making chart
with st.container():
    # Calculate the required data for the charts
    complaints_by_product = filtered_df.groupby('product')['complaint_id'].count().reset_index()
    complaints_by_month = filtered_df.groupby(pd.to_datetime(filtered_df['date_received']).dt.to_period('M'))['complaint_id'].count().reset_index()
    complaints_by_month.rename(columns={'date_received': 'Month Year'}, inplace=True)

    


    bar_chart = alt.Chart(complaints_by_product).mark_bar().encode(
        x='complaint_id',
        y=alt.Y('product', sort='-x')
    )

    line_chart = alt.Chart(complaints_by_month).mark_line().encode(
        x='complaint_id',
        y='Month Year'
    )

    st.write('# Number of Complaints by Product')
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(bar_chart, use_container_width=True)

    
    with col2:
        st.write('# Number of Complaints by MonthYear')
        st.altair_chart(line_chart, use_container_width=True)

with st.container():
    complaints_by_channel = filtered_df.groupby('submitted_via')['complaint_id'].count().reset_index()
    complaints_by_issue = df.groupby(['issue', 'sub_issue']).size().reset_index(name='count')
    

    PieChart= alt.Chart(complaints_by_channel).mark_bar().encode(
      alt.X('count:Q', title='Number of Complaints'),
      alt.Color('index:N', scale=alt.Scale(scheme='category20b')),
      tooltip=['index:N', 'count:Q']
    ).properties(
    width=500,
    height=400,
    title='Number of Complaints by Submitted Via Channel'
)


    fig_treemap = alt.Chart(complaints_by_issue).mark_rect().encode(
    alt.X('issue:N', axis=alt.Axis(title='issue')),
    alt.Y('sub_issue:N', axis=alt.Axis(title='sub_issue')),
    alt.Color('count:Q', scale=alt.Scale(scheme='greens'), title='Number of Complaints'),
    tooltip=[alt.Tooltip('issue:N'), alt.Tooltip('sub_issue:N'), alt.Tooltip('count:Q')]
).properties(
    width=600,
    height=400,
    title='Number Over Complaints by Issue and Sub-Issue'
)


    

    
    col1, col2 = st.columns(2)
    with col1:
        st.write('# Number of Complaints by Submitted via channel')
        st.altair_chart(PieChart)

    
    with col2:
        st.write('# Number of Complaints by Issue and Subissue')
        st.altair_chart(fig_treemap)


# Define the footer content
footer = """
<div style='text-align: center;'>
    <hr>
    <p>Made By <span style='color: #e25555;'></span>Sana Shaikh</p>
</div>
"""


st.markdown(footer, unsafe_allow_html=True)

 

