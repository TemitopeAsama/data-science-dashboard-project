import pandas as pd


class QueryBase:

    # The table this class queries. Subclasses override it.
    name = ''

    # The id column for the table named by `name`. Subclasses
    # override this with `employee_id` or `team_id`.
    id_column = ''

    def names(self):
        return []

    def event_counts(self, id: str) -> pd.DataFrame:
        # Positive and negative event counts per day, ascending by date
        sql_query = f"""
            SELECT
                evt.event_date,
                SUM(evt.positive_events) AS positive_events,
                SUM(evt.negative_events) AS negative_events
            FROM employee_events AS evt
            JOIN {self.name} AS e
                ON evt.{self.id_column} = e.{self.id_column}
            WHERE e.{self.id_column} = ?
            GROUP BY evt.event_date
            ORDER BY evt.event_date ASC
        """

        return self.pandas_query(sql_query, (id,))

    def notes(self, id: str) -> pd.DataFrame:
        # Notes recorded against an entity, joined on the id column
        sql_query = f"""
            SELECT
                n.note_date,
                n.note
            FROM notes AS n
            JOIN {self.name} AS e ON n.{self.id_column} = e.{self.id_column}
            WHERE e.{self.id_column} = ?
        """

        return self.pandas_query(sql_query, (id,))
