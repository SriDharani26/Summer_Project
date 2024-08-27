import streamlit as st
import mysql.connector
import food_reg
import pandas as pd
from fuzzywuzzy import process
from decimal import Decimal

def verify_user(email, password):
    try:
        conn = mysql.connector.connect(
            host='localhost',  
            user='root', 
            password='hemsmysql3', 
            database='food_det'  
        )
        cursor = conn.cursor()
        query = "SELECT name,id FROM food_det WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        return result
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return None

def verify_user_goal(user_id):
    result = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='hemsmysql3',
            database='food_det'
        )
        cursor = conn.cursor()
        query = "SELECT goal FROM goals WHERE uid=%s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone() 
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()
    return result

def log():
    st.title('Login to Food Recognition and Nutrition Analysis')

    # Login form
    st.header('User Login')
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    if st.button('New User? Go to Registration'):
        st.session_state.current_page = 'reg'
        st.experimental_rerun()
    if st.button('Login'):
        if email and password:
            user = verify_user(email, password)
            if user:
                st.success('Login successful!')
                st.session_state.current_page = 'h_main'
                st.session_state.current_user=user
                st.experimental_rerun()
            else:
                st.error('Invalid email or password. Please try again.')
        else:
            st.error('Please enter both email and password.')


def search_food(food_name, df):
    food_name = food_name.lower()
    choices = df['Name'].tolist()
    match, score = process.extractOne(food_name, choices)
    if score >= 80:  # Adjust score threshold as needed
        food_details = df[df['Name'] == match]
        return food_details
    else:
        return pd.DataFrame()


def food_item(fp):
    data = pd.read_csv(fp)
    st.title('Food Nutrient Lookup')
    food_choices = data['Name'].unique().tolist()
    
    # This will hold the selected food name
    food_item = st.selectbox('Enter the name of the food item:', options=food_choices)
    
    if st.button('Submit'):
        if food_item:
            results = search_food(food_item, data)
            if not results.empty:
                # Display the DataFrame without index using st.dataframe()
                st.dataframe(results.style.hide(axis='index'))
            else:
                st.write('Food item not found. Please check the spelling or try another item.')
        else:
            st.write('Please enter a food item.')
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        if st.button('Back'):
            st.session_state.current_page = 'h_main'
            st.experimental_rerun()
    with col2:
        if st.button('Logout'):
            st.session_state.current_page = 'log'
            st.experimental_rerun()

def h_main():
    st.header(f"Hi {st.session_state.current_user[0]}!")

    # Place other buttons in the main column
    col1, col2, col3 = st.columns(3)  # Creates 3 equally spaced columns
    
    with col1:
        if st.button('Nutritional Analysis'):
            st.session_state.current_page = 'food_item'
            st.experimental_rerun()
    
    with col2:
        if st.button('Diet Management'):
            st.session_state.current_page = 'diet'
            st.experimental_rerun()
    
    with col3:
        if st.button('Update Profile'):
            st.session_state.current_page = 'up_prof'
            st.experimental_rerun()
    if st.button('Logout'):
        st.session_state.current_page = 'log'
        st.experimental_rerun()


        

def goal_reg(x,g):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  
            password='hemsmysql3',
            database='food_det'  
        )
        cursor = conn.cursor()
        query = """
        INSERT INTO goals (goal,user_id,uid)
        VALUES (%s, %s,%s)
        """
        cursor.execute(query, (g,x,x))
        conn.commit()
        st.success('Updated')
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def goal_update(x,g):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  
            password='hemsmysql3',
            database='food_det'  
        )
        cursor = conn.cursor()
        query = """UPDATE goals SET goal = %s WHERE user_id = %s """
        cursor.execute(query, (g,x))
        conn.commit()
        st.success('Updated')
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def food_search(f,d):
    f_list=[]
    for i in f:
        food_name = i.lower()
        choices = d['Name'].tolist()
        match, score = process.extractOne(food_name, choices)
        if score >= 70:  
            food_details = d[d['Name'] == match]
            # Select only the necessary columns
            required_columns = ['Protein [g]', 'Fat [g]', 'Carbohydrate [g]', 'Energy [KJ]']
            f_list.append(food_details[required_columns])
    return f_list

def to_float(value):
    try:
        return float(value)
    except ValueError:
        return 0.0


def cal_daily(height, weight, age, sex, activity_level, category):
    height = to_float(height)
    weight = to_float(weight)
    age = to_float(age)
    
    # Harris-Benedict equation for BMR calculation
    if sex == 'Male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Activity factor based on activity level
    activity_factors = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extra active': 1.9
    }
    
    # Calculate TDEE
    tdee = bmr * activity_factors[activity_level]
    
    # Adjust daily caloric goal based on category
    if category == 'Maintain Weight':
        daily_caloric_goal = tdee
    elif category == 'Gain Weight':
        daily_caloric_goal = tdee + 500
    elif category == 'Lose Weight':
        daily_caloric_goal = tdee - 500
    else:
        daily_caloric_goal = tdee  # Default to maintain if unknown category
    return int(daily_caloric_goal)


def calculate_calories(food_t, q):
    res = 0.0
    l = 0
    
    def calculate_meal_calories(protein, fat, carbs, energy_kj, quantity):
        # Convert all inputs to float
        protein = to_float(protein)
        fat = to_float(fat)
        carbs = to_float(carbs)
        energy_kj = to_float(energy_kj)
        quantity = to_float(quantity)
        
        # Convert energy from kJ to kcal
        energy_kcal = energy_kj * 0.239
        
        protein *= quantity
        fat *= quantity
        carbs *= quantity
        energy_kcal *= quantity
        
        calories_from_protein = protein * 3
        calories_from_fat = fat * 7
        calories_from_carbs = carbs * 3
        
        return calories_from_protein + calories_from_fat + calories_from_carbs + energy_kcal
    
    for i in food_t:
        if not i.empty:
            f_cal = calculate_meal_calories(
                i.iloc[0, 0],  # protein
                i.iloc[0, 1],  # fat
                i.iloc[0, 2],  # carbs
                i.iloc[0, 3],  # energy (in kJ)
                q[l]           # quantity
            )
            res += f_cal
            l += 1
            
    return int(res)



def get_det_user(d):
    result = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='hemsmysql3',
            database='food_det'
        )
        cursor = conn.cursor()
        query = "SELECT height,weight,age,gender,act_lvl FROM food_det WHERE id=%s"
        cursor.execute(query, (d,))
        result = cursor.fetchone() 
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()
    return result

def get_us_cat(d):
    result = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='hemsmysql3',
            database='food_det'
        )
        cursor = conn.cursor()
        query = "SELECT goal FROM goals WHERE uid=%s"
        cursor.execute(query, (d,))
        result = cursor.fetchone() 
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()
    return result

def diet(fp):
    st.header('Welcome')
    d=int(st.session_state.current_user[1])
    res=verify_user_goal(d)
    if res:
        st.subheader(f'Your Category: {res[0]}')
        if st.button('Modify'):
            st.session_state.show_modify = True
    
        if 'show_modify' in st.session_state and st.session_state.show_modify:
            goal = st.selectbox('Weight Goal', ['Maintain Weight', 'Lose Weight', 'Gain Weight'])
            if st.button('Update'):
                goal_update(d, goal)
                st.session_state.show_modify = False
                st.session_state.current_page = 'diet'
                st.experimental_rerun()
        if 'bk_list' not in st.session_state:
            st.session_state.bk_list = []
        if 'bkq_list' not in st.session_state:
            st.session_state.bkq_list = []
        if 'ln_list' not in st.session_state:
            st.session_state.ln_list = []
        if 'lnq_list' not in st.session_state:
            st.session_state.lnq_list = []
        if 'dn_list' not in st.session_state:
            st.session_state.dn_list = []
        if 'dnq_list' not in st.session_state:
            st.session_state.dnq_list = []
        data = pd.read_csv(fp)
        food_choices = data['Name'].unique().tolist()
        food_bk = st.selectbox('Enter Your Breakfast', options=food_choices)
        # quantity,cup,grams
        qbn = int(st.number_input('Enter the Quantity for Breakfast', format="%.0f"))
        qb = st.selectbox('BreakFast Quantity', ['Grams', 'Cups', 'Pieces'])
        if st.button('Add BreakFast'):
            if food_bk:
                st.session_state.bk_list.append(food_bk)
                st.session_state.bkq_list.append(qbn)
                st.session_state.food_bk=''
                st.success('Added')
        food_ln = st.selectbox('Enter Your Lunch', options=food_choices)
        qln = int(st.number_input('Enter the Quantity for Lunch', format="%.0f"))
        ql = st.selectbox('Lunch Quantity', ['Grams', 'Cups', 'Pieces'])
        if st.button('Add Lunch'):
            if food_ln:
                st.session_state.ln_list.append(food_ln)
                st.session_state.lnq_list.append(qln)
                st.session_state.food_ln=''
                st.success('Added')
        food_dn = st.selectbox('Enter Your Dinner', options=food_choices)
        qdn = int(st.number_input('Enter the Quantity for Dinner', format="%.0f"))
        qd = st.selectbox('Dinner Quantity', ['Grams', 'Cups', 'Pieces'])
        if st.button('Add Dinner'):
            if food_dn:
                st.session_state.dn_list.append(food_dn)
                st.session_state.dnq_list.append(qdn)
                st.session_state.food_dn=''
                st.success('Added')
        data = pd.read_csv(fp)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button('Calculate'):
                rst1=food_search(st.session_state.bk_list,data)
                rst2=food_search(st.session_state.ln_list,data)
                rst3=food_search(st.session_state.dn_list,data)
                if rst1 or rst2 or rst3:
                        res_det=get_det_user(d)
                        res_det_cat=get_us_cat(d)
                        rs1=0
                        rs2=0
                        rs3=0
                        if st.session_state.bkq_list:
                            rs1=calculate_calories(rst1,st.session_state.bkq_list)
                        if st.session_state.lnq_list:
                            rs2=calculate_calories(rst2,st.session_state.lnq_list)
                        if st.session_state.dnq_list:
                            rs3=calculate_calories(rst3,st.session_state.dnq_list)
                        rs=to_float(rs1)+to_float(rs2)+to_float(rs3)
                        daily_cal=cal_daily(res_det[0],res_det[1],res_det[2],res_det[3],res_det[4],res_det_cat[0])
                        st.write(f'Total Calories Consumed: {rs}')
                        st.write(f'Daily Caloric Goal: {daily_cal}')
                else:
                    st.write('Food item not found. Please check the spelling or try another item.')

    else:
        goal = st.selectbox('Weight Goal', ['Maintain Weight', 'Lose Weight', 'Gain Weight'])
        if st.button('Submit'):
            goal_reg(d,goal)
            st.session_state.current_page = 'diet'
            st.experimental_rerun()
    with col2:
        if st.button('Clear'):
            st.session_state.bk_list = []
            st.session_state.bkq_list = []
            st.session_state.lnq_list = []
            st.session_state.ln_list = []
            st.session_state.dnq_list = []
            st.session_state.dn_list = []
    with col3:
        if st.button('Back'):
            st.session_state.current_page = 'h_main'
            st.experimental_rerun()
    if st.button('Logout'):
        st.session_state.bk_list = []
        st.session_state.bkq_list = []
        st.session_state.lnq_list = []
        st.session_state.ln_list = []
        st.session_state.dnq_list = []
        st.session_state.dn_list = []
        st.session_state.current_page = 'log'
        st.experimental_rerun()
def up_prof():
    inject_css()
    #st.markdown('<div class="profile-update-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="profile-update-title">Update Profile</h1>', unsafe_allow_html=True)

    with st.form(key='update_form', clear_on_submit=True):
        age = st.number_input('Age', min_value=0, max_value=120, step=1)
        height = st.number_input('Height (cm)', min_value=0.0, max_value=300.0, step=0.1, format='%f')
        weight = st.number_input('Weight (kg)', min_value=0.0, max_value=500.0, step=0.1, format='%f')
        act = st.selectbox('Activity Level', ['sedentary', 'lightly active', 'moderately active', 'very active', 'extra active'])

        submit_button = st.form_submit_button('Submit', use_container_width=True)
        if submit_button:
            try:
                conn = mysql.connector.connect(
                    host='localhost',
                    user='root',  
                    password='hemsmysql3',
                    database='food_det'  
                )
                cursor = conn.cursor()
                query = """
                UPDATE food_det SET age=%s, height=%s, weight=%s, act_lvl=%s WHERE id=%s"""
                cursor.execute(query, (age, height, weight, act, st.session_state.current_user[1]))
                conn.commit()

                st.success('User details submitted successfully! Please Refresh the Page')
            except mysql.connector.Error as err:
                st.error(f"Error: {err}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
    
    if st.button('Back'):
        st.session_state.current_page = 'h_main'
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def inject_css():
    with open('style.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def main():
    inject_css()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'log'
    
    if st.session_state.current_page == 'log':
        log()
    elif st.session_state.current_page == 'reg':
        food_reg.reg()
    elif st.session_state.current_page == 'h_main':
        h_main()
    elif st.session_state.current_page == 'food_item':
        food_item('food.csv')
    elif st.session_state.current_page == 'diet':
        diet('food.csv')
    elif st.session_state.current_page == 'up_prof':
        up_prof()


if __name__ == '__main__':
    main()