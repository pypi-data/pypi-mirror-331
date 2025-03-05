'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''
import json
import pandas as pd
from .rest import Rest
from .adp_misc import AdpMisc

class AdpDataframe():
    '''
    classdocs
    '''
    def __init__(self,table_name):
        '''
        Constructor
        '''
        self.utils = AdpMisc()
        self.rest=None
        self.table_name = table_name
        self.query = f"SELECT * FROM {table_name}"  # Default query
        self.conditions = []
        self.selected_columns = ["*"]
        self.group_by_columns = []
        self.aggregations = []
        self.joins = []
        

    def set_rest(self, rest: Rest):
        '''
            Set Rest instance

            @param rest (Rest): rest instance
        '''
        self.rest = rest
        self.utils.set_rest(rest)

    def select(self, *columns):
        """Select specific columns"""
        self.selected_columns = list(columns)
        return self

    def filter(self, condition):
        """Apply a WHERE filter"""
        self.conditions.append(condition)
        return self

    def group_by(self, *columns):
        """Group by specific columns"""
        self.group_by_columns = list(columns)
        return self

    def agg(self, **aggregations):
        """Apply aggregations like SUM, AVG, COUNT"""
        for alias, expr in aggregations.items():
            self.aggregations.append(f"{expr} AS {alias}")
        return self

    def join(self, other, condition):
        """Perform SQL JOIN"""
        join_query = f"JOIN {other.table_name} ON {condition}"
        self.joins.append(join_query)
        return self


    def _build_query(self):
        """Build the final SQL query correctly"""
        base_query = f"SELECT {', '.join(self.selected_columns)} FROM {self.table_name}"

        if self.joins:
            base_query += " " + " ".join(self.joins)

        if self.conditions:
            base_query += " WHERE " + " AND ".join(self.conditions)

        if self.group_by_columns:
            base_query += f" GROUP BY {', '.join(self.group_by_columns)}"

        # Ensure aggregation happens at the correct place
        if self.aggregations:
            query = f"SELECT {', '.join(self.group_by_columns)}, {', '.join(self.aggregations)} FROM ({self.table_name})"

            if self.conditions:
                query += " WHERE " + " AND ".join(self.conditions)
            
           

            if self.group_by_columns:
                query += f" GROUP BY {', '.join(self.group_by_columns)}"

            return query

        return base_query

    def show(self, limit=10):
        """Execute the query and show results"""
        query = self._build_query() + f" FETCH FIRST {limit} ROWS ONLY"
        js = self.utils.run_query(query)
        tn = pd.DataFrame.from_records(js)
        return tn

    def collect(self):
        """Execute query and return all results"""
        query = self._build_query()
        js = self.utils.run_query(query)
        tn = pd.DataFrame.from_records(js)
        return tn

    def explain(self):
        """Show the current SQL query"""
        print("Generated SQL Query:")
        print(self._build_query())

