# Graduation Project Report - Week 1 Draft

**Project:** Replenishment Decision Quality: An Evaluation and Monitoring
Framework for ML-Driven Retail Stock Distribution
**Author:** Kagan Sahin
**Date:** October 2026

> Draft status: initial versions of the required Week 1 sections. These will be
> extended weekly as the project develops.

## 1. Introduction

Machine learning is now used routinely in retail operations, and one of its most
common applications is replenishment: deciding which products, and in what
quantities, should be distributed from central warehouses to individual stores.
A typical replenishment platform combines a sales forecasting model with
business rules such as minimum stock levels, pack sizes, and store priorities,
and produces distribution decisions every day.

Software engineering for such systems does not end at deployment. Like any other
production system, they require continuous evaluation and monitoring. This
project focuses on that often-neglected layer: measuring how good the forecasts
and the resulting replenishment decisions actually are.

## 2. Problem Statement

A production replenishment system produces daily decisions, but the quality of
those decisions is not measured in a structured way. Concretely:

1. **Forecast accuracy is not tracked systematically.** Predictions are compared
   with actual sales only occasionally and informally, so systematic error
   patterns (by store, category, or season) remain invisible.
2. **Decision deviations are unexplained.** When the quantity actually shipped
   differs from the quantity the model asked for, the difference may be caused
   by warehouse stock limits, business-rule constraints, or other factors. Today
   there is no automatic classification of these deviation causes.
3. **Improvement is therefore not targeted.** Without measurement, it is
   impossible to know whether effort should be spent on better models, changed
   business rules, or warehouse operations.

## 3. Motivation

The financial impact of replenishment errors is direct: stock-outs cause lost
sales and dissatisfied customers, while overstock ties up working capital and
shelf space. In seasonal retail, an over-distributed product often cannot be
sold at full price later in the season, so mistakes are expensive and largely
irreversible.

There is also a software engineering motivation. Published industry case studies
report that monitoring and evaluation are among the most commonly neglected
aspects of deployed machine learning systems, and that model performance can
degrade silently without them. A monitoring framework turns the replenishment
system from a black box into a measurable, auditable component.

Finally, the project has a practical constraint that shapes its design: the
realistic data used for validation belongs to an industry partner and cannot be
shared. This motivates a clear separation between code and data, and a synthetic
data generator that makes the entire pipeline reproducible by anyone.

## 4. Project Objective

The objective is to develop an evaluation and monitoring framework for ML-driven
replenishment decisions that:

1. ingests sales, forecast, inventory, and decision records from a SQL data
   source;
2. computes forecast-accuracy metrics (WAPE, MAPE, bias) at store-product level
   and aggregates them by store, product category, and season;
3. compares forecast quantities with final shipped quantities and classifies the
   causes of deviations (stock constraint, rule constraint, other);
4. presents results in an interactive dashboard;
5. includes a synthetic data generator so that all functionality can be
   demonstrated and tested without confidential data.

## 5. Preliminary Scope

### 5.1 In scope (first version)

- Batch evaluation of forecasts and decisions over historical data.
- Metric computation and multi-level aggregation (store, category, season).
- Deviation-cause classification.
- Interactive dashboard for exploring the results.
- Synthetic data generator with known ground truth.
- Unit and integration tests for metric and classification logic.

### 5.2 Out of scope (first version)

- Modifying the production replenishment engine (the project evaluates
  decisions; it does not optimize them).
- Automatic retraining or tuning of forecasting models.
- Real-time or streaming analysis.
- Customer-level analysis and price optimization.
- Multi-company or multi-schema support beyond a configurable SQL connection.
