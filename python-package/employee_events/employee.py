from .query_base import QueryBase
from .sql_execution import QueryMixin


class Employee(QueryBase, QueryMixin):

    name: str = "employee"
    id_column: str = "employee_id"

    def names(self) -> list[tuple]:
        # Full name and id for every employee
        sql_query = f"""
            SELECT (first_name || ' ' || last_name) AS full_name, employee_id
            FROM {self.name}
        """

        return self.query(sql_query)

    def username(self, id: str) -> list[tuple]:
        # Full name for a single employee
        sql_query = f"""
            SELECT (first_name || ' ' || last_name) AS full_name
            FROM {self.name}
            WHERE employee_id = ?
        """

        return self.query(sql_query, (id,))

    # Returns the summed positive and negative event counts,
    # which is the input shape the machine learning model expects
    def model_data(self, id):
        sql_query = f"""
                    SELECT SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = ?
            """

        return self.pandas_query(sql_query, (id,))
