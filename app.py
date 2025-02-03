import streamlit as st
import mysql.connector
import pandas as pd
from datetime import timedelta
import plotly.express as px

# Function to establish the database connection
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    port=3306,
    password='1999',
    database='healthcare_insights',
    auth_plugin='mysql_native_password'
)
mycursor = mydb.cursor(buffered=True)


# Read the Excel file
file_path =("C:/Users/Mers_Johnson/Downloads/Healthcare_Dataset.xlsx")
df= pd.read_excel(file_path)

# Display the first few rows
print(df.head())

print(df.isnull().sum()) #used to check the null values.


from datetime import timedelta

# Assume df is your DataFrame
# Fill missing follow-up dates with 7 days after discharge
df['Followup Date'] = df['Followup Date'].fillna(df['Discharge_Date'] + timedelta(days=7))

print(df['Followup Date'].isnull().sum())  

print(df.isnull().sum())

date_columns = ['Admit_Date', 'Discharge_Date', 'Followup Date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Format datetime columns as strings
for col in date_columns:
    df[col] = df[col].dt.strftime('%Y-%m-%d')

# Verify
print(df)

mycursor.execute('SHOW DATABASES')
for i in mycursor:
    print(i)

    mycursor.execute('USE Healthcare_Insights')
mydb.commit()

#Table Creation
mycursor.execute('''
CREATE TABLE IF NOT EXISTS Healthcare_Insights (
    Patient_ID VARCHAR(50),
    Admit_Date DATE,
    Discharge_Date DATE,
    Diagnosis VARCHAR(255),
    Bed_Occupancy VARCHAR(50),
    Test VARCHAR(255),
    Doctor VARCHAR(100),
    Followup_Date DATE,
    Feedback TEXT,
    Billing_Amount DECIMAL(10, 2),
    Health_Insurance_Amount DECIMAL(10, 2)
)
''')
for i,row in df.iterrows():
    sql="INSERT INTO Healthcare_Insights VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.execute(sql,tuple(row))
    mydb.commit()
mydb.commit()

# Streamlit UI
st.title('HEALTHCARE INSIGHTS DASHBOARD')

# Sidebar navigation with a selectbox for question selection
selected_option = st.selectbox(
    "Select any Question",
    ['Q1. Trends in Admission Over Time',
     'Q2. Seasonal Admission Patterns',
     'Q3. Diagnosis Frequency Analysis',
     'Q4. Bed Occupancy Analysis',
     'Q5. Length of Stay Distribution',
     'Q6. Revenue Analysis',
     'Q7. Diagnosis Wise Revenue Distribution',
     'Q8. Patients Requiring Follow-ups',
     'Q9. Average Billing per Patient',
     'Q10. Insurance Utilization Rate',
     'Q11. Top 5 Doctors by Patient Count',
     'Q12. Top Tests per Diagnosis',
     'Q13. Diagnosis Contribution to Long Stays',
     'Q14. Average Stay per Bed Type',
     'Q15. Monthly Patient Feedback Count']
)

# Function to execute SQL queries
def execute_query(sql, columns):
    mycursor.execute(sql)
    data = mycursor.fetchall()
    return pd.DataFrame(data, columns=columns)

# Query execution and visualization
if selected_option == 'Q1. Trends in Admission Over Time':
    st.header("Trends in Admission Over Time")
    sql = """SELECT DATE_FORMAT(Admit_Date, '%Y-%m') AS month, COUNT(*) AS total_admissions
             FROM Healthcare_Insights GROUP BY DATE_FORMAT(Admit_Date, '%Y-%m') ORDER BY month;"""
    df = execute_query(sql, ['Month', 'Total Admissions'])
    st.dataframe(df)
    st.plotly_chart(px.line(df, x="Month", y="Total Admissions", title="Admission Trends Over Time"))

elif selected_option == 'Q2. Seasonal Admission Patterns':
    st.header("Seasonal Admission Patterns")
    sql = """SELECT EXTRACT(MONTH FROM Admit_Date) AS month, COUNT(*) AS total_admissions
             FROM Healthcare_Insights GROUP BY month ORDER BY month;"""
    df = execute_query(sql, ['Month', 'Total Admissions'])
    st.dataframe(df)
    st.plotly_chart(px.bar(df, x="Month", y="Total Admissions", title="Seasonal Admission Patterns"))

elif selected_option == 'Q3. Diagnosis Frequency Analysis':
    st.header("Diagnosis Frequency Analysis")
    sql = """SELECT Diagnosis, COUNT(*) AS diagnosis_count
             FROM Healthcare_Insights GROUP BY Diagnosis ORDER BY diagnosis_count DESC LIMIT 5;"""
    df = execute_query(sql, ['Diagnosis', 'Diagnosis Count'])
    st.dataframe(df)
    st.plotly_chart(px.bar(df, x="Diagnosis", y="Diagnosis Count", title="Top 5 Diagnoses"))

elif selected_option == 'Q4. Bed Occupancy Analysis':
    st.header("Bed Occupancy Analysis")
    sql = """SELECT Bed_Occupancy, COUNT(*) AS occupancy_count FROM Healthcare_Insights
             GROUP BY Bed_Occupancy ORDER BY occupancy_count DESC;"""
    df = execute_query(sql, ['Bed Occupancy', 'Occupancy Count'])
    st.dataframe(df)
    st.plotly_chart(px.pie(df, names="Bed Occupancy", values="Occupancy Count", title="Bed Occupancy Distribution"))

elif selected_option == 'Q5. Length of Stay Distribution':
    st.header("Length of Stay Distribution")
    sql = """SELECT DATEDIFF(Discharge_Date, Admit_Date) AS length_of_stay
             FROM Healthcare_Insights;"""
    df = execute_query(sql, ['Length of Stay'])
    st.dataframe(df)
    st.plotly_chart(px.histogram(df, x="Length of Stay", title="Length of Stay Distribution"))

elif selected_option == 'Q6. Revenue Analysis':
    st.header("Revenue Analysis")
    sql = """SELECT SUM(Billing_Amount) AS total_revenue,
                    SUM(Health_Insurance_Amount) AS total_insurance_coverage,
                    SUM(Billing_Amount - Health_Insurance_Amount) AS total_out_of_pocket
             FROM Healthcare_Insights;"""
    df = execute_query(sql, ['Total Revenue', 'Total Insurance Coverage', 'Total Out of Pocket'])
    st.dataframe(df)
    df_melted = df.melt(var_name="Category", value_name="Amount")
    st.plotly_chart(px.bar(df_melted, x="Category", y="Amount", title="Revenue Breakdown"))

elif selected_option == 'Q7. Diagnosis Wise Revenue Distribution':
    st.header("Diagnosis Wise Revenue Distribution")
    sql = """SELECT Diagnosis, SUM(Billing_Amount) AS total_revenue
             FROM Healthcare_Insights GROUP BY Diagnosis ORDER BY total_revenue DESC;"""
    df = execute_query(sql, ['Diagnosis', 'Total Revenue'])
    st.dataframe(df)
    st.plotly_chart(px.bar(df, x="Diagnosis", y="Total Revenue", title="Revenue by Diagnosis"))

elif selected_option == 'Q8. Patients Requiring Follow-ups':
    st.header("Patients Requiring Follow-ups")
    sql = """SELECT COUNT(*) AS patients_with_followup, COUNT(*) - COUNT(Followup_Date) AS patients_without_followup
             FROM Healthcare_Insights;"""
    df = execute_query(sql, ['Patients With Follow-up', 'Patients Without Follow-up'])
    st.dataframe(df)
    st.plotly_chart(px.pie(df.melt(), names="variable", values="value", title="Follow-up Rates"))

elif selected_option == 'Q9. Average Billing per Patient':
    st.header("Average Billing per Patient")
    
    sql = """SELECT AVG(Billing_Amount) AS avg_billing_per_patient FROM Healthcare_Insights;"""
    df = execute_query(sql, ['Average Billing Per Patient'])
    
    st.dataframe(df)  # Display data table
    
    # Convert to a readable format (avoid index-based x-axis)
    df['Category'] = 'Average Billing'  
    
    # Bar chart with proper labels
    fig = px.bar(df, 
                 x="Category", 
                 y="Average Billing Per Patient", 
                 title="Average Billing Per Patient",
                 text="Average Billing Per Patient",
                 color="Category",
                 color_discrete_sequence=["#4CAF50"])  # Green color for billing
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')  # Format text
    
    st.plotly_chart(fig)  # Display the bar chart

elif selected_option == 'Q10. Insurance Utilization Rate':
    st.header("Insurance Utilization Rate")
    sql = """SELECT (SUM(Health_Insurance_Amount) / SUM(Billing_Amount)) * 100 AS insurance_coverage_rate
             FROM Healthcare_Insights;"""
    df = execute_query(sql, ['Insurance Coverage Rate (%)'])

    # Display the dataframe
    st.dataframe(df)

    # Calculate the non-coverage rate (100% - insurance coverage rate)
    non_coverage_rate = 100 - df['Insurance Coverage Rate (%)'][0]

    # Prepare data for the pie chart
    pie_data = {
        'Category': ['Insurance Coverage', 'Non-Coverage'],
        'Value': [df['Insurance Coverage Rate (%)'][0], non_coverage_rate]
    }
    pie_df = pd.DataFrame(pie_data)

    # Create and display the pie chart
    st.plotly_chart(px.pie(pie_df, names='Category', values='Value', title="Insurance Utilization Rate"))

elif selected_option == 'Q11. Top 5 Doctors by Patient Count':
    st.header("Top 5 Doctors by Patient Count")
    
    # SQL Query
    sql = """SELECT 
                Doctor,
                COUNT(*) AS patient_count
             FROM Healthcare_Insights
             GROUP BY Doctor
             ORDER BY patient_count DESC
             LIMIT 5;"""
    
    # Execute query and store result in a DataFrame
    df = execute_query(sql, ['Doctor', 'Patient Count'])
    
    # Display data in table format
    st.dataframe(df)
    
    # Bar chart visualization
    fig = px.bar(df, 
                 x="Doctor", 
                 y="Patient Count", 
                 title="Top 5 Doctors by Patient Count", 
                 color="Doctor",
                 text="Patient Count")
    
    # Display bar chart in Streamlit
    st.plotly_chart(fig)
    st.header("Patients with Multiple Diagnoses")
    sql = """SELECT Patient_ID, COUNT(Diagnosis) AS diagnosis_count
             FROM Healthcare_Insights GROUP BY Patient_ID HAVING diagnosis_count > 1 ORDER BY diagnosis_count DESC;"""
    df = execute_query(sql, ['Patient ID', 'Diagnosis Count'])
    st.dataframe(df)
    st.plotly_chart(px.bar(df, x="Patient ID", y="Diagnosis Count", title="Patients with Multiple Diagnoses"))

elif selected_option == 'Q12. Top Tests per Diagnosis':
    st.header("Top Tests per Diagnosis")
    sql = """SELECT Diagnosis, Test, COUNT(*) AS test_count
             FROM Healthcare_Insights GROUP BY Diagnosis, Test ORDER BY Diagnosis, test_count DESC;"""
    df = execute_query(sql, ['Diagnosis', 'Test', 'Test Count'])
    st.dataframe(df)
    st.plotly_chart(px.bar(df, x="Test", y="Test Count", color="Diagnosis", title="Top Tests per Diagnosis"))

elif selected_option == 'Q13. Diagnosis Contribution to Long Stays':
    st.header("Diagnosis Contribution to Long Stays")
    sql = """SELECT Diagnosis, COUNT(*) AS long_stay_count
             FROM Healthcare_Insights WHERE DATEDIFF(Discharge_Date, Admit_Date) > 10
             GROUP BY Diagnosis ORDER BY long_stay_count DESC;"""
    df = execute_query(sql, ['Diagnosis', 'Long Stay Count'])
    st.dataframe(df)
    st.plotly_chart(px.bar(df, x="Diagnosis", y="Long Stay Count", title="Diagnosis and Long Stays"))
elif selected_option == 'Q14. Average Stay per Bed Type':
    st.header("Average Stay per Bed Type")
    
    # SQL Query to get average length of stay per bed type
    sql = """SELECT 
                Bed_Occupancy,
                AVG(DATEDIFF(Discharge_Date, Admit_Date)) AS avg_length_of_stay
             FROM Healthcare_Insights
             GROUP BY Bed_Occupancy
             ORDER BY avg_length_of_stay DESC;"""
    
    # Execute the query
    df = execute_query(sql, ['Bed Occupancy', 'Average Length of Stay (Days)'])
    
    # Display the dataframe
    st.dataframe(df)
    
    # Create and display a bar chart for Average Length of Stay per Bed Type
    st.plotly_chart(px.bar(df, x='Bed Occupancy', y='Average Length of Stay (Days)', 
                           title="Average Length of Stay per Bed Type", 
                           labels={'Average Length of Stay (Days)': 'Average Stay (Days)', 'Bed Occupancy': 'Bed Type'},
                           color='Average Length of Stay (Days)',  # Color the bars based on average length of stay
                           color_continuous_scale='Viridis'))  # Choose a color scale for the bars

elif selected_option == 'Q15. Monthly Patient Feedback Count':
    st.header("Monthly Patient Feedback Count")
    sql = """SELECT DATE_FORMAT(Admit_Date, '%Y-%m') AS month, COUNT(Feedback) AS feedback_count
             FROM Healthcare_Insights GROUP BY month ORDER BY month;"""
    df = execute_query(sql, ['Month', 'Feedback Count'])
    st.dataframe(df)
    st.plotly_chart(px.line(df, x="Month", y="Feedback Count", title="Monthly Feedback Count"))





