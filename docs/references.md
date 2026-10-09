# References (Week 1)

## Academic References

### A1. Another look at measures of forecast accuracy

- **Authors:** Rob J. Hyndman, Anne B. Koehler
- **Year:** 2006
- **Source:** International Journal of Forecasting, 22(4), 679-688
- **DOI:** [10.1016/j.ijforecast.2006.03.001](https://doi.org/10.1016/j.ijforecast.2006.03.001)
- **What I learned:** The paper compares commonly used forecast accuracy measures
  and shows that MAPE has serious weaknesses: it is undefined when actual values
  are zero, and it penalizes over-forecasting more than under-forecasting. In
  retail demand many store-product pairs sell zero units on a given day, so
  dividing by actuals is risky. This directly affects which metrics my framework
  will compute and why weighted absolute percentage error (WAPE) is a safer
  default choice.

### A2. The M5 competition: Background, organization, and implementation

- **Authors:** Spyros Makridakis, Evangelos Spiliotis, Vassilios Assimakopoulos
- **Year:** 2022
- **Source:** International Journal of Forecasting, 38(4), 1325-1336
- **DOI:** [10.1016/j.ijforecast.2021.07.007](https://doi.org/10.1016/j.ijforecast.2021.07.007)
- **What I learned:** The M5 competition forecasted store-item level sales for a
  large retail chain, which is structurally similar to the data domain of this
  project. The paper explains how a large-scale retail forecasting benchmark is
  organized and evaluated (point forecasts with WAPE/RMSSE, plus a separate
  uncertainty track). I will use its evaluation design as a reference for
  structuring my own metric computations and aggregation levels.

### A3. Challenges in Deploying Machine Learning: A Survey of Case Studies

- **Authors:** Andrei Paleyes, Raoul-Gabriel Urma, Neil D. Lawrence
- **Year:** 2022
- **Source:** ACM Computing Surveys, 55(6), Article 114, 1-29
- **DOI:** [10.1145/3533378](https://doi.org/10.1145/3533378)
- **What I learned:** Based on reported industry case studies, the paper shows
  that monitoring and evaluation are among the most commonly neglected parts of
  deployed ML systems, and that model performance can degrade silently without
  them. This motivates the core idea of my project: treating monitoring of a
  deployed replenishment system as a first-class software engineering problem
  rather than an afterthought.

## Technical References

### T1. pandas documentation

- **Organization:** pandas Development Team
- **Year:** continuously updated
- **Link:** [pandas.pydata.org/docs](https://pandas.pydata.org/docs/)
- **What I learned:** The user guide covers the core operations I will need for
  combining sales and forecast records: joining tables on store/product keys,
  grouping and aggregating by multiple dimensions (store, category, date), and
  time-series functionality. pandas will be the main data-processing layer of
  the framework.

### T2. Streamlit documentation

- **Organization:** Streamlit Inc.
- **Year:** continuously updated
- **Link:** [docs.streamlit.io](https://docs.streamlit.io/)
- **What I learned:** Streamlit allows building interactive data applications
  directly in Python. The documentation explains caching (important because
  metric computations over large tables can be expensive) and widgets for
  drill-down filtering. I plan to use it for the monitoring dashboard.

### T3. pytest documentation

- **Organization:** pytest Development Team
- **Year:** continuously updated
- **Link:** [docs.pytest.org](https://docs.pytest.org/)
- **What I learned:** The documentation explains fixtures and parametrized
  tests, which I will use to verify that metric implementations produce correct
  values on small, hand-computed examples before running them on real data.
