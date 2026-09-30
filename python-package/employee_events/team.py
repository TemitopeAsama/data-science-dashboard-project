from .query_base import QueryBase
from .sql_execution import QueryMixin


class Team(QueryBase, QueryMixin):

    name: str = "team"
    id_column: str = "team_id"

    def names(self) -> list[tuple]:
        # Name and id for every team
        sql_query = f"""
            SELECT team_name, team_id
            FROM {self.name}
        """

        return self.query(sql_query)

    def username(self, id: str) -> list[tuple]:
        # Name for a single team
        sql_query = f"""
            SELECT team_name
            FROM {self.name}
            WHERE team_id = ?
        """

        return self.query(sql_query, (id,))

    # Returns per-member positive and negative event counts,
    # one row per employee on the team
    def model_data(self, id):
        sql_query = f"""
            SELECT positive_events, negative_events FROM (
                    SELECT employee_id
                         , SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = ?
                    GROUP BY employee_id
                   )
                """

        return self.pandas_query(sql_query, (id,))
