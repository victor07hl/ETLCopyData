class queries():
    def __init__(self) -> None:
        self.str_sql_count_hired_Q = '''
            with joins as (
            select 
            d.department,
            j.job,
            datepart(QUARTER,cast(h.DATETIME as datetime)) Q
            from stage.hired_employees h
            left join stage.departments d on h.department_id = d.id
            left join stage.jobs j on h.job_id = j.id
            )

            select department,
                    job,
                    [1] Q1,
                    [2] Q2,
                    [3] Q3,
                    [4] Q4
                    --,[1]+[2]+[3]+[4] Tot
            from (
                select department,job,Q from joins
            ) as aux
            pivot 
            (
                count(Q)
                for Q in ([1],[2],[3],[4])
            ) as pivotTable

            order by department, job
        '''

        self.hired_above_mean = '''
                            with aux as (
                            select 
                            d.id,
                            d.department,
                            count(1) as hired
                            from stage.hired_employees h
                            left join stage.departments d on h.department_id = d.id
                            where YEAR(cast(h.DATETIME as datetime)) = 2021
                            group by d.id, d.department
                            )
                            ,
                            h_avg as (

                            select AVG(hired) hired from aux)

                            select * from aux
                            where hired > (select hired from h_avg)
                            order by hired desc
        '''

        