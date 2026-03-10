class queries:
    def __init__(self) -> None:
        self.str_sql_count_hired_Q = """
            WITH joins AS (
                SELECT
                    d.department,
                    j.job,
                    DATEPART(QUARTER, CAST(h.DATETIME AS DATETIME)) AS Q
                FROM stage.hired_employees h
                LEFT JOIN stage.departments d ON h.department_id = d.id
                LEFT JOIN stage.jobs j ON h.job_id = j.id
            )
            SELECT
                department,
                job,
                [1] AS Q1,
                [2] AS Q2,
                [3] AS Q3,
                [4] AS Q4
            FROM (
                SELECT department, job, Q FROM joins
            ) AS aux
            PIVOT (
                COUNT(Q) FOR Q IN ([1], [2], [3], [4])
            ) AS pivot_table
            ORDER BY department, job
        """

        self.hired_above_mean = """
            WITH aux AS (
                SELECT
                    d.id,
                    d.department,
                    COUNT(1) AS hired
                FROM stage.hired_employees h
                LEFT JOIN stage.departments d ON h.department_id = d.id
                WHERE YEAR(CAST(h.DATETIME AS DATETIME)) = 2021
                GROUP BY d.id, d.department
            ),
            h_avg AS (
                SELECT AVG(hired) AS hired FROM aux
            )
            SELECT * FROM aux
            WHERE hired > (SELECT hired FROM h_avg)
            ORDER BY hired DESC
        """
