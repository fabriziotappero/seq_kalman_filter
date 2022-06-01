# Example of implementation of a simple 1D Kalaman Filter
# https://teyvonia.com/kalman-filter-1d-localization-python/

# Istall needed libraries
#
#   python3 -m pip install pandas streamlit

# How to run this script:
#
#    streamlit run seq_kalman_filter.py

import pandas as pd
import streamlit as st
import plotly.express as px
import os

# csv file
FILEPATH = 'data.zip'

st.set_page_config(layout="wide")

def isNaN(num):
    if float('-inf') < float(num) < float('inf'):
        return False 
    else:
        return True

def unwrap(angle):
    ''' converts an angle in the range (0,+360) into
        its equivalent in the range (-180,+180)
    '''
    # do nothing if angle is nan
    if isNaN(angle):
        return angle

    if angle-180 < 0:
        return float(angle) - int((angle-180)/360)*360    
    else:
        return float(angle) - int((angle-180)/360)*360 - 360

class oneD_kalman_filter:
    ''' Implementation of the 1D Kalman filter
    '''
    def __init__(self,initial,std_initial,std_meas,std_noise):
        """   initialize minimum required variables
        
        _in:            initial 'x' value "guess", it 
                        is not important that a precise value is given
                        because the Kalman filter converges quickly
        std_initial:    initial error in estimated "guess"
                        value that is updated every cycle
        std_meas:       measurement error, this is an input that 
                        remains for any update
        std_noise:      process noise. Note that if x does not 
                        changes in real, process noise is zero
        """
        # the first measurement is assigned to the estimated 
        # value because is the best knowledge we have from that variable
        self.out =initial  
        self.p = std_initial**2
        self.r = std_meas**2 + 1E-9
        self.q = std_noise**2
    
    def override(self,_in):
        ''' Override Kalman filter by imposing the filtered value.
            This does not alters std_estimate
        '''
        self.out = _in

    def gain(self):
        ''' Calculation of Kalman gain k
        '''
        self.k = self.p/(self.p + self.r)

    def update(self,_in):
        ''' Update the estimated measurement
            _in: signal to filter
            p  : filtered or estimated value
        '''
        # do not update if _in is nan
        if self.isNaN(_in):
            return self.out

        self.z = _in
        self.out = self.out + self.k*(self.z - self.out)
        self.p = (1-self.k)*self.p
        return self.out
        
    def update_ang(self,_in):
        ''' Update the estimated measurement
            _in: signal to filter. 
            This is a special update function to be used for angular 
            measurements in the range (+/-180 deg).
            output: x or x_e estimated 'x'
            output: p
        '''
        # do not update if _in is nan
        if self.isNaN(_in):
            return self.out
        
        self.z = _in
        self.out = self.unwrap(self.out + self.k*self.unwrap(self.z - self.out))
        self.p = (1-self.k)*self.p
        return self.out

    def prediction(self,model,*args):
        ''' Predict the next state of x
        input: x_p predicted 'x' from dynamic model
        output: x predicted 'x'
        output: p predicted 'p'
        '''
        self.out = model(self.out,*args)
        self.p = self.p + self.q

    def isNaN(self,num):
        if float('-inf') < float(num) < float('inf'):
            return False 
        else:
            return True
        
    def unwrap(self,angle):
        ''' converts an angle in the range (0,+360) into
            its equivalent in the range (-180,+180)
        '''
        if angle-180 < 0:
            return float(angle) - int((angle-180)/360)*360    
        else:
            return float(angle) - int((angle-180)/360)*360 - 360


# Kalman filter model (can't be simpler)
def basic_model(x):
    return x
    
@st.cache()
def load_data(FILEPATH):
    if os.path.exists(FILEPATH):
        df = pd.read_csv(FILEPATH, skiprows = 0)
        return df
   
# not sure why but this cannot be cached...     
#@st.cache()
def load_preview(c1, df, FILEPATH):
    c1.line_chart(df["awa_deg"], height=300)
    c1.write('Complete dataset preview of: *' + FILEPATH + '*')

# load CSV file
df = load_data(FILEPATH)

# setup page 
st.title('Sequential Kalman Filter')
st.write('Implementation of a sequential 1D Kalaman filter. Data is loaded from a local CSV file.')
st.write(' ')

c1,c2 = st.columns(2)

# print out all input data
if c1.checkbox('Show preview.', value=True):
    load_preview(c1, df, FILEPATH)
    
# slider
sig_portion = c2.slider('', 
                        min_value=0, 
                        max_value=84000, 
                        step=2000)
c2.write('Select file section to load.')


# sliders and text
std_meas = c2.slider('', min_value=0, 
                      max_value=1000, value=635, step=1)/1000
                      
c2.write('Filter Model Signal Std Deviation: ' + str(std_meas))
         
std_noise = c2.slider('', min_value=0, 
                       max_value=1000, value=148, step=1)/1000

c2.write('Filter Model Noise Std Deviation: '+ str(std_noise)) 

# let us instantiate the Kalman filter
kf1 = oneD_kalman_filter(0,0, std_meas, std_noise) 

# acquire input
in_sig = []
for x in range(sig_portion,sig_portion+2000): 
    d = df['awa_deg'][x].astype(float).round(2)
    # d = unwrap(d) # transform 
    in_sig.append(d)

out_sig = []
for _in in in_sig:
   kf1.prediction(basic_model)
   kf1.gain()
   x = kf1.update_ang(_in)
   out_sig.append(x)

c1 = st.columns(1)

# large plot (two different plot libraries can be used)
if True:
    # plot using Plotly
    chart_data = pd.DataFrame({'in_sig':in_sig, 'filtered_sig':out_sig}) 
    fig = px.line(chart_data)
    fig.update_layout( xaxis_title="Number of Samples", yaxis_title="",
                       legend_title="Signals",legend=dict(yanchor="top",
                       y=0.99,xanchor="left",x=0.01))
                       
    st.plotly_chart(fig, use_container_width=True)
else:
    # plot using Streamlit Plot 
    chart_data = pd.DataFrame({'in_sig':in_sig, 'filtered_sig':out_sig}) 
    st.line_chart(chart_data, height=300)

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)
