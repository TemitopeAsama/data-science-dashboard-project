# Import any dependencies needed to execute sql queries
import pandas as pd

# Define a class called QueryBase
# Use inheritance to add methods
# for querying the employee_events database.
class QueryBase:

    # Create a class attribute called `name`
    # set the attribute to an empty string
    name = ''

    # Define a `names` method that receives
    # no passed arguments
    def names(self):
        
        # Return an empty list
        return []


    # Define an `event_counts` method
    # that receives an `id` argument
    # This method should return a pandas dataframe
    def event_counts(self, id: str) -> pd.DataFrame:

        # QUERY 1
        # Write an SQL query that groups by `event_date`
        # and sums the number of positive and negative events
        # Use f-string formatting to set the FROM {table}
        # to the `name` class attribute
        # Use f-string formatting to set the name
        # of id columns used for joining
        # order by the event_date column
        sql_query = f"""
            SELECT
                event_date,
                SUM(CASE WHEN event_type = 'positive' THEN 1 ELSE 0 END) as positive_events,
                SUM(CASE WHEN event_type = 'negative' THEN 1 ELSE 0 END) as negative_events
            FROM {self.name}
            WHERE {self.id_column} = ?
            GROUP BY event_date
            ORDER BY event_date ASC
        """

        return pd.read_sql_query(sql_query, self.connection, params=(id,))
            
    

    # Define a `notes` method that receives an id argument
    # This function should return a pandas dataframe
    def notes(self, id: str) -> pd.DataFrame:

        # QUERY 2
        # Write an SQL query that returns `note_date`, and `note`
        # from the `notes` table
        # Set the joined table names and id columns
        # with f-string formatting
        # so the query returns the notes
        # for the table name in the `name` class attribute
        sql_query = f"""
            SELECT
                n.note_date,
                n.note
            FROM notes AS n
            JOIN {self.name} AS e ON n.{self.id_column} = e.{self.id_column}
            WHERE e.{self.id_column} = ?
        """
        return pd.read_sql_query(sql_query, self.connection, params=(id,))

    

