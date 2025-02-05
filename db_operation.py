from sqlalchemy import text
async def  execute_query(db, query: str, params=None):
    print(f"Execute Query:\n {query} \nParams: {params}")
    """
    parameters : 
    - query : sql query
    - params : {"key": "value"}
    - db : sqlalchemy.ext.asyncio.AsyncSession
    """

    if params is None:
        result = await db.execute(text(query))
    else:
        result = await db.execute(text(query), params)

    return result

