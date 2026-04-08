import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sb
import warnings
from streamlit_option_menu import option_menu
warnings.filterwarnings("ignore")

# set a page name for web app
st.set_page_config(page_title="To Do App", layout="wide", page_icon="📅")

# creates three columns in the ratio of 1:2:1 and in second column put title so that title seems centre aligned keep other columns unused
# a, b, c = st.columns([1, 1, 1])
# b.title("To Do App")

# using streamlit_option_menu it shows attractive menu button for our menu options
with st.sidebar:
   nav=option_menu("To Do App Navigation",["Create","Show","Manage(marking complete)","Insights","Settings","About"],menu_icon="geo",icons=["building","eye","journal-check","graph-up","gear","info"],default_index=5)
   

# if tap on create button it will perform this action defined below
if nav == "Create":
    st.title("Create")
    # use form function in streamlit doing so after entering each value it doesn't rerun every time, after that it run only once when submit button is pressed
    with st.form(key="form1"):
        d, e = st.columns(2)
        sd = d.date_input("Start date")
        ed = e.date_input("End date")
        tk = st.text_input("Enter tasks like this : Gym,Study,Play")
        submit = st.form_submit_button("Submit")
    
    # if submit button pressed taking all these values it create a dataframe and also save this dataframe into current directory
    if submit:
        try:
            start_date = sd.strftime("%Y-%m-%d")
            end_date = ed.strftime("%Y-%m-%d")
            task_list = tk

            date_range = pd.date_range(start=start_date, end=end_date)
            dates = [d.strftime("%Y-%m-%d") for d in date_range]

            tasks = [t.strip() for t in task_list.split(",")]
            tasks= [x.title() for x in tasks]

            data = pd.DataFrame(index=dates, columns=tasks)
            data.index= pd.to_datetime(data.index)
            data.to_csv("app_data.csv")

            st.success("Data Saved Successfully!")
            # st.table(data)

        except Exception as e:
            st.error(f"Error: {e}")

# if show button pressed it excess the saved location that created in "create" section and shows whole data of csv file in table form
elif nav == "Show":
    st.title("Data")
    try:
        df = pd.read_csv("app_data.csv", index_col=0)
        st.table(df)
    except FileNotFoundError:
        st.error("File not found. Please create a To Do list first.")

# if pressed on manage button it will create a new window to manage tasks
elif nav=="Manage(marking complete)":
    st.title("Mark Task")
    try:
        df = pd.read_csv("app_data.csv", index_col=0)
        dfcl=df.columns.tolist()
        
        
        tskmng=st.radio("Choose task",dfcl,index=None)
        x, y = st.columns(2)
        tdchoice=x.button(":green[For Today]")
        ytdchoice=y.button(":red[For Yesterday]")
        td=date.today()
        tdstr=str(td)
        ytd=td-timedelta(days=1) # using timedelta function subtract 1 day from today
        ytdstr=str(ytd)

        # if both conditions true than add task for today
        if tdchoice and tskmng:
          st.write(f"You added task : {tskmng} for {tdstr}")
          df.loc[tdstr,tskmng]=1
          df.to_csv("app_data.csv")
    
        # if both conditions true than add task for yesterday
        if ytdchoice and tskmng:
          st.write(f"You added task : {tskmng} for {ytdstr}")
          df.loc[ytdstr,tskmng]=1
          df.to_csv("app_data.csv")
        st.table(df[:tdstr])
            

    except RuntimeError:
        st.error("Error in task managing")

# if pressed on insights show a new radio button for choosing input to which analysis you want to see
elif nav=="Insights":
    st.title("Insights")
    df=pd.read_csv("app_data.csv",index_col=0)

    idv=df.index[0]
    idvstr=str(idv)
    td=date.today()
    tdstr=str(td)
    tdx=df.index.get_loc(tdstr)
    df=df[:tdstr]
    id_list=df.index.to_list()
    cl_list=df.columns.to_list()
    cl_count=df.shape[1]+1
    ind_count=df.shape[0]+1
    indxsum=df.sum(axis=1)
    clsum=df.sum(axis=0)
    clsums=clsum.sort_values(ascending=False)
    
    tdcount=int(df.loc[tdstr].sum())
    totalcol=df.shape[1]
    totalindex=df.shape[0]
    td_pct=tdcount/totalcol*100
    nul_col=df.loc[tdstr][df.loc[tdstr].isnull()].index.tolist()
    cmp_col=df.loc[tdstr][df.loc[tdstr].notnull()].index.tolist()
    names=[f"Completed:{cmp_col}",f"Pending:{nul_col}"]
    
    # creates a selectbox input and saves values into a new variable
    insbox=st.selectbox("Select Charts to see Insight",["Today's Progress","Day Wise Tracker","Task Accuracy"],index=None)
    
    
    if insbox=="Today's Progress":
      # pie chart
      fig = px.pie(df,names=names, values=[tdcount,totalcol-tdcount],title="Today's progress Report")
      st.plotly_chart(fig)
    
    if insbox=="Day Wise Tracker":
      # stacked column chart
      fig1, ax1 = plt.subplots(figsize=(10,10))
      df.plot(kind="bar",stacked=True, ax=ax1, edgecolor="black")
      # creates a for loop in which container variable finds container stores in ax1.container and col finds in df.columns,
      # and return there values to the lables and labels only work when you did more than 0 zero tasks for a single day and gives name to all stacked conatiner
      for container, col in zip(ax1.containers, df.columns):
          labels = [col if v > 0 else "" for v in container.datavalues]
          ax1.bar_label(container, labels=labels, label_type='center', fontsize=10)
      ax1.set_title(f"Date Wise Task Completions from {idvstr} to {tdstr}")
      ax1.set_ylim(0,cl_count)
      st.pyplot(fig1)

    if insbox=="Task Accuracy":
      # bar graph for task accuracy
      fig2,ax2 =plt.subplots(figsize=(10,10))
      clsums.plot(kind="bar", ax=ax2, edgecolor="black" )
      # enumerate function works to find values from a dictionary where i find key values of dict and v returns the value of matched key
      for i,v in enumerate(clsums):
          plt.text(i, v+0.01,str(f"{int(v/totalindex*100)}%"), ha="center", va="bottom", fontsize=10)
      ax2.set_title("Task Accuracy")
      ax2.get_yaxis().set_visible(False)
    #   ax2.set_ylim(0,ind_count)
      plt.xlabel("Tasks")
      plt.ylabel("Frequency")
      st.pyplot(fig2)
    
    
# this feature is added for manual task completion only for past dates
elif nav=="Settings":
   st.title("Settings")
   st.info("Add task for back date only when you forgot to tick but task is completed.")
   df=pd.read_csv("app_data.csv",index_col=0)
   stdvalue=df.index[0]
   td=date.today()
   tdstr=str(td)
   cl_list=df.columns.tolist()
   with st.form(key="form3"):
      tskmng=st.radio("Select Task",cl_list,index=None)
      dtinput=st.date_input("Enter Date")
      submit3=st.form_submit_button("Submit")
   if submit3:
      dtinput=dtinput.strftime("%Y-%m-%d")
      if dtinput<stdvalue:
         st.write("Date entered is not found. please re select a date from current To Do Date range")
      elif dtinput<tdstr:
         df.loc[dtinput,tskmng]=1
         df.to_csv("app_data.csv")
      elif dtinput>tdstr:
         st.write("You can not complete future tasks. Select a date from past") 
      st.table(df[:tdstr])


elif nav=="About":
   st.title("About")
   st.write("In this web app you can create your task, manage daily to do tasks and see insights of your tasks in interactive graphs.")
   st.write(" > Once create a To Do Calender for a days/months/year. No need to create again untill you want to add a new task for rest of days")
   st.write(" > Can add new tasks anytime with same dates, if use different dates for new task additon it will recreate a new database leading to lost old data in this situtaion if you want to keep old data that take a photo before creating new TODO and complete tasks manually in backdate. Manual task completion feature is available in SETTINGS button")
   st.write(" > In case you missed to complete yesterday's task in TODO App but you completed the task than tap on YESTERDAY button in Manage Task feature")
   st.write(" > If you want to delete data base of the ToDo App then find file name of [app_data] in csv format in google colab files section")
   st.write(" > If your current cycle(a month/week/specific_days) of to do calender is completed and you want to save this file for future comparison than rename this file and create new to do calender cycle")


# it addes a footer using CSS 
#    st.markdown(
#     """
#     <style>
#     .footer {
#         position: fixed;
#         left: 0;
#         bottom: 0;
#         width: 100%;
#         background-color: transparent;
#         color: white;
#         text-align: center;
#         padding: 10px;
#         font-size: 16px;
#     }
#     </style>
#     <div class="footer">
#          Created by Hanu Rao
#     </div>
#     """,
#     unsafe_allow_html=True
# )
   
# it adds a footer to sidebar, just below the option menu   
st.sidebar.markdown(
    """
    <div class="sidebar-footer" style="
        margin-top:auto;
        text-align:center;
        padding:10px;
        font-size:14px;
        font-weight:bold;
        font-style:italic; /* italic font */
        background: transparent;
        color:white;
        border-radius:5px;">
           Made with ❤️ in India 
    </div>
    """,
    unsafe_allow_html=True
)
