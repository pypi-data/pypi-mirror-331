from __future__ import annotations

import ast
import datetime as dt
import os

import pandas as pd
import requests

from tetsu.src import cloudant_helper


def workday_extraction(input_date: dt.datetime | str,
                       cloudant_doc: dict = None) -> str:
    """Extracts the workday from the epm workday calendar.
    Example:
        today = dt.datetime.now()
        wd = workday_extraction(today)

    :param input_date (str or timestamp): expects a date as string or timestamp
    :param cloudant_doc: Cloudant document for credentials retrieval

    :returns: workday
    """
    if cloudant_doc is None:
        cloudant_doc = ast.literal_eval(os.getenv("cloudant_document"))

    try:
        # ---- Extract JSON ----------------------------------------------------------------------------#
        creds = cloudant_helper.get_credentials(doc=cloudant_doc, creds={"api_key": ["workday_calendar_api_key"]})

        custom_dates_url = 'https://production.epm-web-platform.dal.app.cirrus.ibm.com/api/calendar/allCustomDates?key='  # noqa: E501
        raw_json = requests.get(custom_dates_url + creds["api_key"], timeout=600).json()

        # ---- Convert JSON to Dataframe ---------------------------------------------------------------#
        df_list = []
        for item in raw_json:
            last_change_epm = dt.datetime.fromtimestamp(item['manipulated'] / 1_000)
            custom_date_name = str(item['customDateName']).upper()

            for date in item['dates']:
                df_list.append({
                    'custom_date_name': custom_date_name,
                    'date': pd.to_datetime(date),
                    'last_change_epm': last_change_epm
                })

        df = pd.DataFrame(df_list)

        # ---- Extract Workday -------------------------------------------------------------------------#
        # Covers all bases by converting to timestamp and normalizing
        clean_date = pd.Timestamp(input_date).normalize()

        try:
            # Convert String to Timestamp and Normalize time component
            workday = df.loc[df.date == clean_date]['custom_date_name'].item()

        except Exception:
            workday = None

        return workday

    except Exception as e:
        print('Workday Calendar Failed\n')
        raise e
