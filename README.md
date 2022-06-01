# Sequential Kalman Filter
Implementation of a 1D Kalman filter suitable to be used in a sequential matter as if used in real time inside an embedded system.

The implementation of this filter requires no libraries. However, to be able to play our with it *streamlit* is used.

Install needed library with:

    python3 -m pip install streamlit pandas plotly


Run the code with:

    streamlit run seq_kalman_filter.py


you can play around with the two parameters of the signal noise mode. Notice that data is taken from a local CSV dataset with a lot of samples.

enjoy.

<p align="center">
  <img src="https://github.com/fabriziotappero/seq_kalman_filter/blob/master/screenshot.jpg?raw=true" alt="" width="90%"/>
</p>